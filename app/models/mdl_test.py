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
    def validate_descripcion(cls, value):
        if len(value) < 2 or len(value) > 50:
            raise ValueError("La descripcion debe tener entre 2 y 50 caracteres.")
        return value

class TestListRequest(BaseModel):
    page: int = Field(default=1)
    nombre: Optional[str] = Field(default=None)
    fecha_actualizacion: date = Field(default=None)

    @field_validator("page")
    def validate_ids(cls, value):
        if value is not None and value <= 0:
            raise ValueError(
                "Número de la página para la paginación, debe ser mayor o igual a 1."
            )
        return value

    @field_validator("fecha_actualizacion")
    def validate_fecha_registro(cls, value):
        if isinstance(value, str):
            try:
                value = date.fromisoformat(value)
            except ValueError:
                raise ValueError(
                    "La fecha de registro debe tener el formato YYYY-MM-DD."
                )
        return value

