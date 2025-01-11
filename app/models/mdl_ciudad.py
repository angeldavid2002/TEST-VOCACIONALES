from typing import Optional
from pydantic import BaseModel, Field


class Ciudad(BaseModel):
    id: int
    nombre: str
    latitud: float
    longitud: float

class CiudadCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    latitud: float
    longitud: float    

class CiudadUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    latitud: Optional[float]
    longitud: Optional[float]