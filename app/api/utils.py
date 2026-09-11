"""Utilidades geográficas usadas para convertir una ruta en zonas del modelo."""

from __future__ import annotations

import math
from typing import Sequence


Coordenada = tuple[float, float]


def haversine_distance(coord1: Coordenada, coord2: Coordenada) -> float:
    """Calcula la distancia entre dos coordenadas WGS84, en kilómetros."""

    radio_tierra_km = 6371.0
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return radio_tierra_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def interpolar_punto(p1: Coordenada, p2: Coordenada, fraccion: float) -> Coordenada:
    """Interpola linealmente un punto entre dos coordenadas cercanas."""

    return (
        p1[0] + (p2[0] - p1[0]) * fraccion,
        p1[1] + (p2[1] - p1[1]) * fraccion,
    )


def distancia_polyline(puntos: Sequence[Coordenada]) -> float:
    """Suma la distancia de todos los segmentos de una polilínea."""

    return sum(haversine_distance(a, b) for a, b in zip(puntos, puntos[1:]))


def densificar_polyline(
    puntos: Sequence[Coordenada], separacion_maxima_m: float = 100.0
) -> list[Coordenada]:
    """Agrega puntos para detectar con precisión los cambios entre clusters."""

    if len(puntos) < 2:
        return list(puntos)

    resultado = [puntos[0]]
    separacion_km = separacion_maxima_m / 1000

    for inicio, fin in zip(puntos, puntos[1:]):
        distancia_km = haversine_distance(inicio, fin)
        divisiones = max(1, math.ceil(distancia_km / separacion_km))
        resultado.extend(
            interpolar_punto(inicio, fin, paso / divisiones)
            for paso in range(1, divisiones + 1)
        )

    return resultado


def punto_medio_polyline(puntos: Sequence[Coordenada]) -> Coordenada:
    """Obtiene el punto ubicado a la mitad de la distancia de una polilínea."""

    if not puntos:
        raise ValueError("La polilínea no contiene puntos.")
    if len(puntos) == 1:
        return puntos[0]

    distancia_total = distancia_polyline(puntos)
    objetivo = distancia_total / 2
    acumulada = 0.0

    for inicio, fin in zip(puntos, puntos[1:]):
        distancia = haversine_distance(inicio, fin)
        if acumulada + distancia >= objetivo and distancia > 0:
            return interpolar_punto(inicio, fin, (objetivo - acumulada) / distancia)
        acumulada += distancia

    return puntos[-1]


def _frontera_entre_zonas(
    inicio: Coordenada,
    fin: Coordenada,
    zona_inicio: int,
    asignar_zona,
    iteraciones: int = 16,
) -> Coordenada:
    """Aproxima por búsqueda binaria el límite entre dos zonas vecinas."""

    izquierda, derecha = inicio, fin
    for _ in range(iteraciones):
        medio = interpolar_punto(izquierda, derecha, 0.5)
        if asignar_zona(*medio) == zona_inicio:
            izquierda = medio
        else:
            derecha = medio
    return interpolar_punto(izquierda, derecha, 0.5)


def segmentar_por_zona(
    puntos: Sequence[Coordenada],
    asignar_zona,
    separacion_maxima_m: float = 100.0,
) -> list[dict]:
    """Divide la ruta cuando cambia el cluster de entrenamiento más cercano.

    Los centroides representan las 150 zonas aprendidas durante el modelado.
    La densificación evita que una línea larga salte una zona sin detectarla.
    """

    puntos_densos = densificar_polyline(puntos, separacion_maxima_m)
    if len(puntos_densos) < 2:
        return []

    zona_actual = asignar_zona(*puntos_densos[0])
    puntos_actuales = [puntos_densos[0]]
    tramos: list[dict] = []

    for anterior, punto in zip(puntos_densos, puntos_densos[1:]):
        zona_punto = asignar_zona(*punto)
        if zona_punto == zona_actual:
            puntos_actuales.append(punto)
            continue

        frontera = _frontera_entre_zonas(
            anterior, punto, zona_actual, asignar_zona
        )
        puntos_actuales.append(frontera)
        tramos.append({"zona": int(zona_actual), "puntos": puntos_actuales})

        zona_actual = zona_punto
        puntos_actuales = [frontera, punto]

    if len(puntos_actuales) > 1:
        tramos.append({"zona": int(zona_actual), "puntos": puntos_actuales})

    return _unir_transiciones_cortas(tramos)


def _unir_transiciones_cortas(tramos: list[dict], minimo_km: float = 0.08) -> list[dict]:
    """Elimina oscilaciones A-B-A muy cortas junto al límite de dos clusters."""

    if len(tramos) < 3:
        return tramos

    resultado: list[dict] = []
    indice = 0
    while indice < len(tramos):
        if (
            indice + 2 < len(tramos)
            and tramos[indice]["zona"] == tramos[indice + 2]["zona"]
            and distancia_polyline(tramos[indice + 1]["puntos"]) < minimo_km
        ):
            unido = {
                "zona": tramos[indice]["zona"],
                "puntos": (
                    tramos[indice]["puntos"]
                    + tramos[indice + 1]["puntos"][1:]
                    + tramos[indice + 2]["puntos"][1:]
                ),
            }
            resultado.append(unido)
            indice += 3
        else:
            resultado.append(tramos[indice])
            indice += 1
    return resultado


def segundos_a_texto(segundos: float) -> str:
    """Convierte segundos a una duración breve y legible."""

    minutos = max(1, round(segundos / 60))
    horas, minutos = divmod(minutos, 60)
    if horas and minutos:
        return f"{horas} h {minutos} min"
    if horas:
        return f"{horas} h"
    return f"{minutos} min"
