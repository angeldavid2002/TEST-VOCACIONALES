from typing import Optional
from pydantic import BaseModel, Field


class Ciudad(BaseModel):
    id: int
    nombre: str
    latitud: float
    longitud: float

class CiudadCreate(BaseModel):
    nombre: str 
    latitud: float
    longitud: float    

class CiudadUpdate(BaseModel):
    nombre: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None