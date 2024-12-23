from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ResenaCreate(BaseModel):
    comentario: str = Field(default="stringst")
    puntuacion: int = Field(default=1)

    @field_validator("comentario")
    def validate_comentario(cls, value):
        if not isinstance(value, str):
            raise ValueError("El comentario debe ser un texto válido.")
        if len(value) < 5:
            raise ValueError("El comentario debe tener al menos 5 caracteres.")
        if len(value) > 500:
            raise ValueError("El comentario no puede exceder los 500 caracteres.")
        return value

    @field_validator("puntuacion")
    def validate_puntuacion(cls, value):
        if not isinstance(value, int):
            raise ValueError("La puntuación debe ser un número entero.")
        if value < 1 or value > 5:
            raise ValueError("La puntuación debe estar entre 1 y 5.")
        return value
