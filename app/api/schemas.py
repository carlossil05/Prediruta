from pydantic import BaseModel, Field

class SolicitudRuta(BaseModel):
    origen: str = Field(..., example="Universidad Nacional de Colombia, Bogotá")
    destino: str = Field(..., example="Parque de la 93, Bogotá")
    fecha_salida: str = Field(..., example="2026-10-25")
    hora_salida: str = Field(..., example="14:30")