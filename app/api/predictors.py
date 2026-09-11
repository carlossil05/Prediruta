"""Carga y contrato de inferencia de los dos modelos productivos."""

from __future__ import annotations

import math
from pathlib import Path

import joblib
import pandas as pd
from pyproj import Transformer


RUTA_MODELOS = Path(__file__).resolve().parents[1] / "modelo"
RUTA_MODELO_OCURRENCIA = RUTA_MODELOS / "modelo_ocurrencia_temporal.joblib"
RUTA_METADATA_OCURRENCIA = RUTA_MODELOS / "metadata_ocurrencia_temporal.joblib"
RUTA_MODELO_ESTADO = RUTA_MODELOS / "modelo_estado_actor_xgboost.joblib"
RUTA_METADATA_ESTADO = RUTA_MODELOS / "metadata_estado_actor.joblib"

for ruta in (
    RUTA_MODELO_OCURRENCIA,
    RUTA_METADATA_OCURRENCIA,
    RUTA_MODELO_ESTADO,
    RUTA_METADATA_ESTADO,
):
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el artefacto requerido: {ruta}")

modelo_ocurrencia = joblib.load(RUTA_MODELO_OCURRENCIA)
metadata_ocurrencia = joblib.load(RUTA_METADATA_OCURRENCIA)
modelo_estado = joblib.load(RUTA_MODELO_ESTADO)
metadata_estado = joblib.load(RUTA_METADATA_ESTADO)

_wgs84_a_bogota = Transformer.from_crs(
    "EPSG:4326", "EPSG:3116", always_xy=True
)
_tamano_celda_m = 500


def validar_contratos_modelos() -> None:
    """Falla al iniciar si un modelo no coincide con su metadata."""

    columnas_ocurrencia = list(metadata_ocurrencia["columnas_entrada"])
    columnas_estado = list(metadata_estado["columnas_entrada"])
    if list(modelo_ocurrencia.feature_names_in_) != columnas_ocurrencia:
        raise RuntimeError("El modelo de ocurrencia no coincide con su metadata.")
    if list(modelo_estado.feature_names_in_) != columnas_estado:
        raise RuntimeError("El modelo de estado no coincide con su metadata.")


validar_contratos_modelos()


def predecir_ocurrencia(zona: int, momento, clima: dict) -> float:
    """Calcula el score espacio-temporal; no es una probabilidad individual."""

    registro = {
        "ZONA_CIUDAD": zona,
        "MES": momento.month,
        "DIA_SEMANA": momento.weekday(),
        "HORA": momento.hour,
        "TEMPERATURA_2M": clima["temperatura"],
        "PRECIPITACION": clima["precipitacion"],
        "NUBOSIDAD": clima["nubosidad"],
        "PRESION_SUPERFICIE": clima["presion"],
        "VELOCIDAD_VIENTO_10M": clima["velocidad_viento"],
        "DIRECCION_VIENTO_10M_SIN": clima["direccion_viento_sin"],
        "DIRECCION_VIENTO_10M_COS": clima["direccion_viento_cos"],
    }
    columnas = metadata_ocurrencia["columnas_entrada"]
    entrada = pd.DataFrame([registro], columns=columnas)
    return float(modelo_ocurrencia.predict_proba(entrada)[0, 1])


def _variables_ciclicas(momento) -> dict:
    valores = {}
    for nombre, valor, periodo in (
        ("MES", momento.month, 12),
        ("DIA_SEMANA", momento.weekday(), 7),
        ("HORA", momento.hour, 24),
    ):
        angulo = 2 * math.pi * valor / periodo
        valores[f"{nombre}_SIN"] = math.sin(angulo)
        valores[f"{nombre}_COS"] = math.cos(angulo)
    return valores


def predecir_estado_actor(
    latitud: float,
    longitud: float,
    zona: int,
    momento,
    perfil: dict,
) -> dict[str, float]:
    """Estima el estado condicional del actor usando el perfil informado."""

    x_bogota, y_bogota = _wgs84_a_bogota.transform(longitud, latitud)
    registro = {
        "CELDA_X": math.floor(x_bogota / _tamano_celda_m),
        "CELDA_Y": math.floor(y_bogota / _tamano_celda_m),
        "EDAD": perfil["edad"],
        **_variables_ciclicas(momento),
        "MES": momento.month,
        "DIA_SEMANA": momento.weekday(),
        "HORA": momento.hour,
        "ZONA_CIUDAD": zona,
        "GENERO": perfil["genero"],
        "CLASE_VEHICULO": perfil["clase_vehiculo"],
        "SERVICIO_VEHICULO": perfil["servicio_vehiculo"],
    }
    columnas = metadata_estado["columnas_entrada"]
    entrada = pd.DataFrame([registro], columns=columnas)
    probabilidades = modelo_estado.predict_proba(entrada)[0]

    catalogo = metadata_estado["catalogo_estados"]
    originales = metadata_estado["clases_originales"]
    clases_modelo = list(modelo_estado.classes_)
    resultado = {}
    for clase_codificada, clase_original in zip(clases_modelo, originales):
        posicion = clases_modelo.index(clase_codificada)
        resultado[catalogo[int(clase_original)]] = float(probabilidades[posicion])
    return resultado
