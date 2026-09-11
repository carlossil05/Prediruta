"""Esquemas de entrada y validaciones visibles también en la documentación API."""

from datetime import date, time

from pydantic import BaseModel, Field, field_validator, model_validator


class PerfilActor(BaseModel):
    """Datos operativos requeridos por el modelo de estado del actor."""

    edad: int = Field(..., ge=0, le=110, examples=[35])
    genero: int = Field(..., ge=0, le=2, examples=[2])
    clase_vehiculo: int = Field(..., ge=0, le=21, examples=[13])
    servicio_vehiculo: int = Field(..., ge=0, le=4, examples=[3])


class Coordenada(BaseModel):
    """Ubicación exacta elegida con Google Places en el frontend."""

    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)


class SolicitudRuta(BaseModel):
    origen: str = Field(..., min_length=3, max_length=200)
    destino: str = Field(..., min_length=3, max_length=200)
    fecha_salida: date
    hora_salida: time
    origen_coordenadas: Coordenada | None = None
    destino_coordenadas: Coordenada | None = None
    perfil_actor: PerfilActor
    consentimiento_datos: bool

    @field_validator("origen", "destino")
    @classmethod
    def limpiar_direccion(cls, valor: str) -> str:
        return " ".join(valor.split())

    @model_validator(mode="after")
    def validar_solicitud(self):
        if self.origen.casefold() == self.destino.casefold():
            raise ValueError("El origen y el destino deben ser diferentes.")
        if not self.consentimiento_datos:
            raise ValueError(
                "Debes aceptar el uso temporal de los datos para ejecutar la consulta."
            )
        return self
