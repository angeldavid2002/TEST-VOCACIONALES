from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Respuesta(BaseModel):
    id: int
    pregunta_id: int
    respuesta: str
    vocacion: str


# Modelo para crear una nueva respuesta
class RespuestaCreate(BaseModel):
    pregunta_id: int = Field(default=1)
    respuesta: str = Field(default="respuesta")
    vocacion: str = Field(default="vocacion")

    @field_validator("pregunta_id")
    def validate_pregunta_id(cls, value):
        if not isinstance(value, int):
            raise ValueError("el id debe ser un número entero.")
        return value

    @field_validator("respuesta")
    def validate_respuesta(cls, value):
        if len(value) < 2 or len(value) > 100:
            raise ValueError("La respuesta debe tener entre 2 y 100 caracteres.")
        return value

    @field_validator("vocacion")
    def validate_vocacion(cls, value):
        if len(value) < 2 or len(value) > 50:
            raise ValueError("La vocación debe tener entre 2 y 50 caracteres.")
        return value


# Modelo para actualizar una respuesta existente
class RespuestaUpdate(BaseModel):
    respuesta_id: int = Field(default=1)
    respuesta: Optional[str] = Field(
        default=None, description="Texto de la respuesta a actualizar."
    )
    vocacion: Optional[str] = Field(
        default=None, description="Vocación asociada a la respuesta a actualizar."
    )

    @field_validator("respuesta_id")
    def validate_respuesta_id(cls, value):
        if not isinstance(value, int):
            raise ValueError("el id debe ser un número entero.")
        return value

    @field_validator("respuesta")
    def validate_respuesta(cls, value):
        if value is not None and (len(value) < 2 or len(value) > 100):
            raise ValueError("La respuesta debe tener entre 2 y 100 caracteres.")
        return value

    @field_validator("vocacion")
    def validate_vocacion(cls, value):
        if value is not None and (len(value) < 2 or len(value) > 50):
            raise ValueError("La vocación debe tener entre 2 y 50 caracteres.")
        return value
