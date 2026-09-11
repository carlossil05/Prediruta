"""Acceso a Google Routes, Google Weather y a las zonas del modelo."""

from __future__ import annotations

import math
import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import requests


RUTA_MODELOS = Path(__file__).resolve().parents[1] / "modelo"
RUTA_CENTROIDES = RUTA_MODELOS / "centroides_zonas.csv"
RUTA_NODOS_CLIMA = RUTA_MODELOS / "nodos_clima_entrenamiento.csv"
GOOGLE_ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
GOOGLE_WEATHER_URL = "https://weather.googleapis.com/v1/forecast/hours:lookup"
GOOGLE_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
GRAVEDAD = 9.80665
MASA_MOLAR_AIRE = 0.0289644
CONSTANTE_GASES = 8.314462618


class ServicioExternoError(RuntimeError):
    """Error controlado de una API externa."""


@lru_cache(maxsize=512)
def obtener_referencia_vial(latitud: float, longitud: float) -> str | None:
    """Convierte una coordenada en una calle y sector comprensibles.

    Se usa únicamente en los sectores destacados. La geocodificación no forma
    parte de la predicción y, si falla, el análisis principal sigue disponible.
    """

    api_key = os.getenv("GOOGLE_APIKEY")
    if not api_key:
        return None
    try:
        respuesta = requests.get(
            GOOGLE_GEOCODING_URL,
            params={
                "latlng": f"{latitud},{longitud}",
                "key": api_key,
                "language": "es",
                "region": "co",
            },
            timeout=10,
        )
        datos = respuesta.json()
    except (requests.RequestException, ValueError):
        return None
    if not respuesta.ok or datos.get("status") != "OK":
        return None

    resultados = datos.get("results", [])
    resultado = resultados[0] if resultados else None
    if not resultado:
        return None
    componentes = resultado.get("address_components", [])

    def componente(*tipos: str) -> str | None:
        for item in componentes:
            if set(tipos) & set(item.get("types", [])):
                return item.get("long_name")
        return None

    via = componente("route", "intersection")
    numero = componente("street_number")
    sector = componente("neighborhood", "sublocality_level_1", "sublocality")
    if via and numero:
        via = f"{via} {numero}"
    if via and sector and via.casefold() != sector.casefold():
        return f"{via}, {sector}"
    if via or sector:
        return via or sector

    direccion = resultado.get("formatted_address", "").split(", Bogotá")[0].strip()
    return direccion or None


for ruta_requerida in (RUTA_CENTROIDES, RUTA_NODOS_CLIMA):
    if not ruta_requerida.exists():
        raise FileNotFoundError(f"No se encontró el archivo requerido: {ruta_requerida}")

_centroides = pd.read_csv(RUTA_CENTROIDES)
_latitudes = _centroides["LATITUD_CENTROIDE"].to_numpy()
_longitudes = _centroides["LONGITUD_CENTROIDE"].to_numpy()
_zonas = _centroides["ZONA_CIUDAD"].to_numpy()
_nodos_clima = pd.read_csv(RUTA_NODOS_CLIMA)
_latitudes_clima = _nodos_clima["LATITUD_NODO"].to_numpy()
_longitudes_clima = _nodos_clima["LONGITUD_NODO"].to_numpy()
_elevaciones_clima = _nodos_clima["ELEVACION_NODO_M"].to_numpy()


def obtener_zona_mas_cercana(latitud: float, longitud: float) -> int:
    """Asigna una coordenada al mismo centroide usado por los modelos."""

    distancias = (_latitudes - latitud) ** 2 + (_longitudes - longitud) ** 2
    return int(_zonas[np.argmin(distancias)])


def distancia_centroide_mas_cercano_km(latitud: float, longitud: float) -> float:
    """Aproxima la distancia al centroide más cercano para validar cobertura."""

    indice = int(
        np.argmin((_latitudes - latitud) ** 2 + (_longitudes - longitud) ** 2)
    )
    lat_media = math.radians((latitud + _latitudes[indice]) / 2)
    delta_lat = (latitud - _latitudes[indice]) * 111.32
    delta_lon = (longitud - _longitudes[indice]) * 111.32 * math.cos(lat_media)
    return float(math.hypot(delta_lat, delta_lon))


def _segundos_google(valor: str) -> float:
    """Convierte el formato Duration de Google, por ejemplo 123.5s."""

    if not valor or not valor.endswith("s"):
        raise ServicioExternoError("Google Routes no devolvió una duración válida.")
    return float(valor[:-1])


def _waypoint_direccion(direccion: str) -> dict:
    return {"address": direccion}


def _waypoint_coordenada(coordenada: tuple[float, float]) -> dict:
    latitud, longitud = coordenada
    return {
        "location": {
            "latLng": {"latitude": latitud, "longitude": longitud}
        }
    }


def _consultar_google_routes(
    origen: dict,
    destino: dict,
    departure_time: datetime,
    intermedios: list[dict] | None = None,
) -> dict:
    """Realiza una consulta reproducible a Compute Routes con tráfico."""

    api_key = os.getenv("GOOGLE_APIKEY")
    if not api_key:
        raise ServicioExternoError(
            "La API no tiene configurada la variable GOOGLE_APIKEY."
        )

    cuerpo = {
        "origin": origen,
        "destination": destino,
        "intermediates": intermedios or [],
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "departureTime": (
            departure_time.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        ),
        "computeAlternativeRoutes": False,
        "polylineQuality": "HIGH_QUALITY",
        "polylineEncoding": "ENCODED_POLYLINE",
        "languageCode": "es-CO",
        "regionCode": "CO",
        "units": "METRIC",
    }
    campos = ",".join(
        [
            "routes.distanceMeters",
            "routes.duration",
            "routes.polyline.encodedPolyline",
            "routes.legs.distanceMeters",
            "routes.legs.duration",
            "routes.legs.polyline.encodedPolyline",
            "routes.legs.startLocation",
            "routes.legs.endLocation",
            "routes.warnings",
        ]
    )
    try:
        respuesta = requests.post(
            GOOGLE_ROUTES_URL,
            json=cuerpo,
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": campos,
            },
            timeout=20,
        )
    except requests.RequestException as error:
        raise ServicioExternoError(
            "No fue posible conectarse con Google Routes."
        ) from error

    if not respuesta.ok:
        try:
            detalle = respuesta.json().get("error", {}).get("message")
        except ValueError:
            detalle = None
        raise ServicioExternoError(
            detalle or f"Google Routes respondió con estado {respuesta.status_code}."
        )

    rutas = respuesta.json().get("routes", [])
    if not rutas:
        raise ServicioExternoError(
            "Google Routes no encontró un recorrido válido para esos puntos."
        )
    return rutas[0]


def obtener_ruta_base_google(
    origen: str,
    destino: str,
    departure_time: datetime,
    origen_coordenadas: tuple[float, float] | None = None,
    destino_coordenadas: tuple[float, float] | None = None,
) -> dict:
    """Obtiene geometría, distancia y duración iniciales del recorrido."""

    ruta = _consultar_google_routes(
        (
            _waypoint_coordenada(origen_coordenadas)
            if origen_coordenadas
            else _waypoint_direccion(origen)
        ),
        (
            _waypoint_coordenada(destino_coordenadas)
            if destino_coordenadas
            else _waypoint_direccion(destino)
        ),
        departure_time,
    )
    leg = ruta["legs"][0]
    return {
        "polyline": ruta["polyline"]["encodedPolyline"],
        "distancia_m": int(ruta["distanceMeters"]),
        "duracion_s": _segundos_google(ruta["duration"]),
        "inicio": leg["startLocation"]["latLng"],
        "fin": leg["endLocation"]["latLng"],
        "advertencias": ruta.get("warnings", []),
        "proveedor": "routes_v2",
    }


def obtener_tiempos_google_por_tramo(
    tramos: list[dict], departure_time: datetime
) -> list[dict]:
    """Pide a Google la duración de cada tramo delimitado por clusters.

    Una consulta con waypoints devuelve un leg por tramo. Si la ruta cruza más
    de 26 zonas, se usan consultas sucesivas porque Google limita a 25 los
    waypoints intermedios.
    """

    if not tramos:
        return []

    if len(tramos) <= 26:
        intermedios = [
            _waypoint_coordenada(tramo["puntos"][-1])
            for tramo in tramos[:-1]
        ]
        ruta = _consultar_google_routes(
            _waypoint_coordenada(tramos[0]["puntos"][0]),
            _waypoint_coordenada(tramos[-1]["puntos"][-1]),
            departure_time,
            intermedios,
        )
        legs = ruta.get("legs", [])
        if len(legs) != len(tramos):
            raise ServicioExternoError(
                "Google Routes no devolvió un tiempo para cada tramo."
            )
        return [
            {
                "duracion_s": _segundos_google(leg["duration"]),
                "distancia_m": int(leg["distanceMeters"]),
            }
            for leg in legs
        ]

    resultados = []
    hora_tramo = departure_time
    for tramo in tramos:
        ruta = _consultar_google_routes(
            _waypoint_coordenada(tramo["puntos"][0]),
            _waypoint_coordenada(tramo["puntos"][-1]),
            hora_tramo,
        )
        duracion = _segundos_google(ruta["duration"])
        resultados.append(
            {
                "duracion_s": duracion,
                "distancia_m": int(ruta["distanceMeters"]),
            }
        )
        hora_tramo = datetime.fromtimestamp(
            hora_tramo.timestamp() + duracion, tz=hora_tramo.tzinfo
        )
    return resultados


def _elevacion_climatica_mas_cercana(latitud: float, longitud: float) -> float:
    """Usa la elevación del nodo climático empleado durante el entrenamiento."""

    indice = int(
        np.argmin(
            (_latitudes_clima - latitud) ** 2
            + (_longitudes_clima - longitud) ** 2
        )
    )
    return float(_elevaciones_clima[indice])


def _presion_superficie(
    presion_nivel_mar: float, temperatura_c: float, elevacion_m: float
) -> float:
    """Convierte la presión de Google a la escala empleada por el modelo.

    Google informa presión a nivel del mar, mientras el entrenamiento usa
    presión superficial. La ecuación hipsométrica emplea la elevación del nodo
    climático histórico más cercano.
    """

    temperatura_kelvin = temperatura_c + 273.15
    exponente = -(
        GRAVEDAD * MASA_MOLAR_AIRE * elevacion_m
    ) / (CONSTANTE_GASES * temperatura_kelvin)
    return presion_nivel_mar * math.exp(exponente)


def _cantidad_precipitacion_mm(registro: dict) -> float:
    qpf = registro.get("precipitation", {}).get("qpf", {})
    cantidad = float(qpf.get("quantity", 0.0))
    if qpf.get("unit") == "INCHES":
        return cantidad * 25.4
    return cantidad


def _consultar_pronostico_google(
    latitud: float, longitud: float, hora_paso: datetime
) -> list[dict]:
    """Obtiene las páginas horarias necesarias hasta el momento solicitado."""

    api_key = os.getenv("GOOGLE_APIKEY")
    if not api_key:
        raise ServicioExternoError(
            "La API no tiene configurada la variable GOOGLE_APIKEY."
        )

    ahora_utc = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    objetivo_utc = hora_paso.astimezone(timezone.utc)
    horas = max(
        1,
        math.ceil((objetivo_utc - ahora_utc).total_seconds() / 3600) + 1,
    )
    if horas > 240:
        raise ServicioExternoError(
            "La hora solicitada supera las 240 horas disponibles en Google Weather."
        )

    parametros = {
        "key": api_key,
        "location.latitude": latitud,
        "location.longitude": longitud,
        "hours": horas,
        "pageSize": min(24, horas),
        "unitsSystem": "METRIC",
        "languageCode": "es-419",
    }
    pronosticos = []
    while True:
        try:
            respuesta = requests.get(
                GOOGLE_WEATHER_URL, params=parametros, timeout=20
            )
            datos = respuesta.json()
        except (requests.RequestException, ValueError) as error:
            raise ServicioExternoError(
                "No fue posible conectarse con Google Weather."
            ) from error

        if not respuesta.ok:
            detalle = datos.get("error", {}).get("message")
            raise ServicioExternoError(
                detalle
                or f"Google Weather respondió con estado {respuesta.status_code}."
            )

        pronosticos.extend(datos.get("forecastHours", []))
        token = datos.get("nextPageToken")
        if not token:
            break
        parametros["pageToken"] = token

    if not pronosticos:
        raise ServicioExternoError(
            "Google Weather no devolvió pronóstico para el tramo."
        )
    return pronosticos


def obtener_clima_tramo(
    latitud: float, longitud: float, hora_paso: datetime
) -> dict:
    """Consulta Google Weather en el punto y momento central del tramo."""

    pronosticos = _consultar_pronostico_google(latitud, longitud, hora_paso)
    objetivo_utc = hora_paso.astimezone(timezone.utc)
    try:
        registro = min(
            pronosticos,
            key=lambda item: abs(
                (
                    datetime.fromisoformat(
                        item["interval"]["startTime"].replace("Z", "+00:00")
                    )
                    - objetivo_utc
                ).total_seconds()
            ),
        )
        temperatura = float(registro["temperature"]["degrees"])
        nubosidad = float(registro["cloudCover"])
        presion_nivel_mar = float(
            registro["airPressure"]["meanSeaLevelMillibars"]
        )
        velocidad_viento = float(registro["wind"]["speed"]["value"])
        direccion = float(registro["wind"]["direction"]["degrees"])
        hora_pronostico = datetime.fromisoformat(
            registro["interval"]["startTime"].replace("Z", "+00:00")
        ).astimezone(hora_paso.tzinfo)
    except (KeyError, TypeError, ValueError) as error:
        raise ServicioExternoError(
            "Google Weather no devolvió todas las variables requeridas por el modelo."
        ) from error

    elevacion = _elevacion_climatica_mas_cercana(latitud, longitud)
    condicion = (
        registro.get("weatherCondition", {})
        .get("description", {})
        .get("text", "Sin descripción")
    )
    return {
        "condicion": condicion,
        "temperatura": temperatura,
        "precipitacion": _cantidad_precipitacion_mm(registro),
        "probabilidad_precipitacion": float(
            registro.get("precipitation", {})
            .get("probability", {})
            .get("percent", 0.0)
        ),
        "nubosidad": nubosidad,
        "presion": _presion_superficie(
            presion_nivel_mar, temperatura, elevacion
        ),
        "presion_nivel_mar": presion_nivel_mar,
        "elevacion_referencia_m": elevacion,
        "velocidad_viento": velocidad_viento,
        "direccion_viento_grados": direccion,
        "direccion_viento_sin": math.sin(math.radians(direccion)),
        "direccion_viento_cos": math.cos(math.radians(direccion)),
        "hora_pronostico": hora_pronostico.isoformat(),
        "modelo": "Google Weather API",
        "latitud_modelo": latitud,
        "longitud_modelo": longitud,
    }
