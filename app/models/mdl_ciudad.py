from pydantic import BaseModel


class Ciudad(BaseModel):
    id: int
    nombre: str
    latitud: float
    longitud: float