"""API principal de PrediRuta.

El modelo de ocurrencia combina ubicación, momento y clima para construir una
comparación relativa con patrones históricos. El estado del actor es una lectura
condicionada a que ocurra un siniestro; ninguna salida representa la probabilidad
individual de sufrir uno.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import polyline
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Permite ejecutar Uvicorn directamente en desarrollo. En Railway las
# variables del servicio conservan prioridad sobre este archivo local.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from api.predictors import (
    metadata_estado,
    metadata_ocurrencia,
    predecir_estado_actor,
    predecir_ocurrencia,
)
from api.schemas import SolicitudRuta
from api.services import (
    ServicioExternoError,
    ajustar_tiempos_a_duracion_total,
    distancia_centroide_mas_cercano_km,
    obtener_clima_tramo,
    obtener_referencia_vial,
    obtener_ruta_base_google,
    obtener_tiempos_google_por_tramo,
    obtener_zona_mas_cercana,
)
from api.utils import punto_medio_polyline, segundos_a_texto, segmentar_por_zona


ZONA_BOGOTA = ZoneInfo("America/Bogota")
DIAS_PRONOSTICO = 7
# Las zonas se construyeron sobre el área urbana. Un margen de 2,5 km tolera
# bordes de los clusters sin admitir atajos amplios por Cota o municipios vecinos.
DISTANCIA_MAXIMA_CENTROIDE_KM = 2.5
UMBRAL_MODELO_OCURRENCIA = float(metadata_ocurrencia["umbral_clasificacion"])


app = FastAPI(
    title="API PrediRuta",
    version="4.0.0",
    description=(
        "Similitud relativa con patrones históricos de siniestros por zona y momento, "
        "incorporando clima de Google Weather, tiempos de Google Routes y estado "
        "condicional del actor en los niveles altos."
    ),
)


def clasificar_criticidad(score: float, destacado: bool = False) -> dict:
    """Traduce la salida binaria del modelo a una jerarquía visual honesta.

    El umbral procede de la validación del artefacto. El nivel alto se reserva
    para hasta tres patrones detectados con mayor score dentro del recorrido;
    no constituye un segundo umbral global ni una probabilidad individual.
    """

    if score < UMBRAL_MODELO_OCURRENCIA:
        return {"nivel": "Bajo", "color": "#2E8B57"}
    if destacado:
        return {"nivel": "Alto", "color": "#D1495B"}
    return {"nivel": "Medio", "color": "#F4A261"}


def validar_horizonte(departure_time: datetime) -> None:
    """Impide consultas fuera del horizonte operativo de siete días."""

    ahora = datetime.now(ZONA_BOGOTA)
    fecha_maxima = ahora.date() + timedelta(days=DIAS_PRONOSTICO - 1)
    # El selector trabaja con precisión de minutos. Aceptamos el minuto actual
    # aunque, al enviar el formulario, ya hayan transcurrido algunos segundos.
    if departure_time < ahora.replace(second=0, microsecond=0):
        raise HTTPException(
            status_code=422,
            detail="La salida no puede estar en el pasado.",
        )
    if departure_time.date() > fecha_maxima:
        raise HTTPException(
            status_code=422,
            detail=(
                "La fecha supera el horizonte de PrediRuta. Solo se permiten "
                f"consultas hasta {fecha_maxima.isoformat()}."
            ),
        )


def validar_cobertura_bogota(tramos: list[dict]) -> None:
    """Comprueba todos los puntos de la ruta, no solo sus extremos."""

    puntos_control = [
        punto
        for tramo in tramos
        for punto in tramo["puntos"]
    ]
    distancia_maxima = max(
        distancia_centroide_mas_cercano_km(*punto) for punto in puntos_control
    )
    if distancia_maxima > DISTANCIA_MAXIMA_CENTROIDE_KM:
        raise HTTPException(
            status_code=422,
            detail=(
                "Google propuso un recorrido que sale del área urbana de Bogotá. "
                "PrediRuta no puede procesarlo porque sus modelos solo cubren la "
                "ciudad. Prueba otro origen, destino u hora de salida."
            ),
        )


def validar_puntos_solicitud(data: SolicitudRuta) -> None:
    """Rechaza origen o destino fuera de la cobertura antes de llamar a Google."""

    for nombre, coordenada in (
        ("origen", data.origen_coordenadas),
        ("destino", data.destino_coordenadas),
    ):
        if coordenada and distancia_centroide_mas_cercano_km(
            coordenada.latitud, coordenada.longitud
        ) > DISTANCIA_MAXIMA_CENTROIDE_KM:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"El {nombre} está fuera del área urbana de Bogotá "
                    "cubierta por PrediRuta. Elige una ubicación dentro de la ciudad."
                ),
            )


def construir_ubicaciones_tramos(
    contextos: list[dict], origen: str, destino: str
) -> list[dict[str, str]]:
    """Nombra los límites reales de todos los tramos en orden de recorrido.

    El origen y el destino conservan los nombres seleccionados por el usuario.
    Los límites internos se describen con geocodificación inversa. Si Google
    Geocoding no responde, se muestran las coordenadas en vez de sustituirlas
    por un nombre de zona que no le explica al usuario dónde está el tramo.
    """

    if not contextos:
        return []

    limites = [contextos[0]["puntos"][0]] + [
        contexto["puntos"][-1] for contexto in contextos
    ]
    claves_internas = list(
        dict.fromkeys(
            (round(latitud, 5), round(longitud, 5))
            for latitud, longitud in limites[1:-1]
        )
    )
    nombres_internos: dict[tuple[float, float], str | None] = {}
    if claves_internas:
        with ThreadPoolExecutor(
            max_workers=min(6, len(claves_internas))
        ) as ejecutor:
            nombres_internos = dict(
                zip(
                    claves_internas,
                    ejecutor.map(
                        lambda punto: obtener_referencia_vial(*punto),
                        claves_internas,
                    ),
                )
            )

    nombres_limites = [origen]
    for latitud, longitud in limites[1:-1]:
        clave = (round(latitud, 5), round(longitud, 5))
        nombres_limites.append(
            nombres_internos.get(clave)
            or f"{latitud:.5f}, {longitud:.5f}"
        )
    nombres_limites.append(destino)

    return [
        {"desde": nombres_limites[indice], "hasta": nombres_limites[indice + 1]}
        for indice in range(len(contextos))
    ]


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "API PrediRuta operativa",
        "version": app.version,
        "horizonte_dias": DIAS_PRONOSTICO,
        "modelos": {
            "ocurrencia": metadata_ocurrencia["modelo"],
            "estado_actor": metadata_estado["modelo"],
        },
    }


@app.post("/predict")
def predecir_ruta(data: SolicitudRuta):
    """Construye una consulta completa sin almacenar los datos recibidos."""

    try:
        departure_time = datetime.combine(
            data.fecha_salida, data.hora_salida, tzinfo=ZONA_BOGOTA
        )
        validar_horizonte(departure_time)
        validar_puntos_solicitud(data)

        # Primera consulta: Google define la ruta que se analizará.
        ruta_google = obtener_ruta_base_google(
            data.origen,
            data.destino,
            departure_time,
            (
                (
                    data.origen_coordenadas.latitud,
                    data.origen_coordenadas.longitud,
                )
                if data.origen_coordenadas
                else None
            ),
            (
                (
                    data.destino_coordenadas.latitud,
                    data.destino_coordenadas.longitud,
                )
                if data.destino_coordenadas
                else None
            ),
        )
        puntos_ruta = polyline.decode(ruta_google["polyline"])
        tramos = segmentar_por_zona(puntos_ruta, obtener_zona_mas_cercana)
        if not tramos:
            raise HTTPException(
                status_code=422,
                detail="La geometría de la ruta no contiene tramos evaluables.",
            )
        validar_cobertura_bogota(tramos)

        # Segunda consulta: los límites de los clusters se envían como waypoints.
        # Así Google calcula una duración específica para cada tramo.
        tiempos_google = ajustar_tiempos_a_duracion_total(
            obtener_tiempos_google_por_tramo(tramos, departure_time),
            ruta_google["duracion_s"],
        )

        hora_acumulada = departure_time
        contextos = []
        for tramo, tiempo in zip(tramos, tiempos_google):
            hora_inicio = hora_acumulada
            hora_fin = hora_inicio + timedelta(seconds=tiempo["duracion_s"])
            punto_representativo = punto_medio_polyline(tramo["puntos"])
            contextos.append(
                {
                    **tramo,
                    **tiempo,
                    "hora_inicio": hora_inicio,
                    "hora_fin": hora_fin,
                    # Google entrega la duración del leg A→A1. Su hora de
                    # llegada a A1 es el momento usado por clima y modelos.
                    "hora_modelo": hora_fin,
                    "punto_representativo": punto_representativo,
                }
            )
            hora_acumulada = hora_fin

        # Las consultas meteorológicas son independientes y se paralelizan.
        with ThreadPoolExecutor(max_workers=min(6, len(contextos))) as ejecutor:
            climas = list(
                ejecutor.map(
                    lambda contexto: obtener_clima_tramo(
                        *contexto["punto_representativo"],
                        contexto["hora_modelo"],
                    ),
                    contextos,
                )
            )

        # Cada fila enviada al modelo usa su esquema productivo completo. El
        # ranking se calcula después de obtener todos los scores para destacar
        # como máximo tres tramos detectados dentro de esta ruta.
        scores = [
            predecir_ocurrencia(
                contexto["zona"], contexto["hora_modelo"], clima
            )
            for contexto, clima in zip(contextos, climas)
        ]
        detectados = [
            indice
            for indice, score in enumerate(scores)
            if score >= UMBRAL_MODELO_OCURRENCIA
        ]
        prioritarios = sorted(
            detectados, key=lambda indice: scores[indice], reverse=True
        )[:3]
        ranking_prioridad = {
            indice: posicion
            for posicion, indice in enumerate(prioritarios, start=1)
        }
        cinco_mayores = sorted(
            range(len(scores)), key=lambda indice: scores[indice], reverse=True
        )[:5]
        ranking_general = {
            indice: posicion
            for posicion, indice in enumerate(cinco_mayores, start=1)
        }

        # Cada tramo recibe un origen y un destino comprensibles. Esto se hace
        # para toda la ruta, no solo para los elementos destacados de la vista.
        ubicaciones_tramos = construir_ubicaciones_tramos(
            contextos, data.origen, data.destino
        )

        perfil = data.perfil_actor.model_dump()
        detalle_tramos = []
        for indice_cero, (contexto, clima, score) in enumerate(
            zip(contextos, climas, scores)
        ):
            indice = indice_cero + 1
            destacado = indice_cero in ranking_prioridad
            criticidad = clasificar_criticidad(score, destacado)
            estado_actor = None
            if destacado:
                probabilidades_estado = predecir_estado_actor(
                    *contexto["punto_representativo"],
                    contexto["zona"],
                    contexto["hora_modelo"],
                    perfil,
                )
                estado_actor = {
                    "tipo": "estimación condicional",
                    "probabilidades": {
                        nombre: round(valor, 4)
                        for nombre, valor in probabilidades_estado.items()
                    },
                    "estado_mas_probable": max(
                        probabilidades_estado, key=probabilidades_estado.get
                    ),
                    "nota": (
                        "Describe el estado del actor si ocurriera un siniestro; "
                        "no estima que el siniestro vaya a ocurrir."
                    ),
                }

            detalle_tramos.append(
                {
                    "tramo": indice,
                    "zona_modelo": contexto["zona"],
                    "puntos_polyline": contexto["puntos"],
                    "hora_inicio": contexto["hora_inicio"].isoformat(),
                    "hora_fin": contexto["hora_fin"].isoformat(),
                    "hora_modelo": contexto["hora_modelo"].isoformat(),
                    "hora_paso": (
                        f'{contexto["hora_inicio"].strftime("%H:%M")} - '
                        f'{contexto["hora_fin"].strftime("%H:%M")}'
                    ),
                    "duracion": segundos_a_texto(contexto["duracion_s"]),
                    "duracion_segundos": round(contexto["duracion_s"]),
                    "distancia_metros": contexto["distancia_m"],
                    "punto_representativo": {
                        "lat": contexto["punto_representativo"][0],
                        "lng": contexto["punto_representativo"][1],
                    },
                    "clima": clima,
                    "score_criticidad": round(score, 4),
                    "umbral_modelo": round(UMBRAL_MODELO_OCURRENCIA, 4),
                    "patron_detectado": score >= UMBRAL_MODELO_OCURRENCIA,
                    "prioridad_recorrido": ranking_prioridad.get(indice_cero),
                    "ranking_recorrido": ranking_general.get(indice_cero),
                    "ubicacion_tramo": ubicaciones_tramos[indice_cero],
                    "nivel_criticidad": criticidad["nivel"],
                    "color": criticidad["color"],
                    "estado_actor": estado_actor,
                }
            )

        score_maximo = max(t["score_criticidad"] for t in detalle_tramos)
        nivel_maximo = "Alto" if prioritarios else "Bajo"
        # La ETA visible siempre corresponde a la ruta principal calculada por
        # Google. El reparto por tramos ya cierra contra esta misma duración.
        duracion_total = ruta_google["duracion_s"]
        return {
            "resumen": {
                "distancia_total_km": round(ruta_google["distancia_m"] / 1000, 1),
                "duracion_estimada": segundos_a_texto(duracion_total),
                "hora_llegada": hora_acumulada.isoformat(),
                "total_tramos": len(detalle_tramos),
                "criticidad_maxima": nivel_maximo,
                "score_maximo": score_maximo,
                "umbral_modelo": round(UMBRAL_MODELO_OCURRENCIA, 4),
                "patrones_detectados": len(detectados),
                "tramos_altos": sum(
                    t["nivel_criticidad"] == "Alto" for t in detalle_tramos
                ),
                "start_location": ruta_google["inicio"],
                "end_location": ruta_google["fin"],
                "fuente_tiempos": "Google Routes API con estimación alta de tráfico",
                "fuente_clima": "Google Weather API",
            },
            "alcance": {
                "interpretacion": (
                    "El modelo indica si detecta un patrón de ocurrencia mediante "
                    "el umbral validado. Entre los detectados se resaltan hasta "
                    "tres scores máximos de la ruta; no son probabilidades individuales."
                ),
                "clima": (
                    "Las variables meteorológicas alimentan el modelo de ocurrencia, "
                    "pero su asociación no demuestra que el clima cause un siniestro."
                ),
                "estado_actor": (
                    "Solo se calcula en tramos altos y está condicionado a que "
                    "ocurra un siniestro."
                ),
                "privacidad": (
                    "Los datos adicionales se usan en memoria para esta consulta "
                    "y no se almacenan."
                ),
            },
            "tramos": detalle_tramos,
        }

    except HTTPException:
        raise
    except ServicioExternoError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error interno al analizar la ruta.",
        ) from error
