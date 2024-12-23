from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Test(BaseModel):
    id: int
    nombre: str
    descripcion: str
    fecha_creacion: Optional[date] = None
    fecha_actualizacion: Optional[date] = None

class TestCreate(BaseModel):
    nombre: str = Field(default="stringst")
    descripcion: str = Field(default="stringst")
    
    @field_validator("nombre")
    def validate_nombre(cls, value):
        if len(value) < 2 or len(value) > 50:
            raise ValueError("El nombre debe tener entre 2 y 50 caracteres.")
        return value
    
    @field_validator("descripcion")
    def validate_nombre(cls, value):
        if len(value) < 2 or len(value) > 50:
            raise ValueError("La descripcion debe tener entre 2 y 50 caracteres.")
        return value