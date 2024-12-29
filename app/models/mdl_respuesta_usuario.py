from typing import Optional
from pydantic import BaseModel, Field, field_validator


class RespuestaDeUsuario(BaseModel):
    id: int
    test_id: int
    respuesta_id: int
    usuario_id: int


# Modelo para crear una nueva respuesta de usuario
class RespuestaDeUsuarioCreate(BaseModel):
    test_id: int = Field(default=1)
    pregunta_id: int = Field(default=1)
    respuesta_id: int = Field(default=1)

    @field_validator("test_id")
    def validate_test_id(cls, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError("El ID del test debe ser un número entero positivo.")
        return value

    @field_validator("pregunta_id")
    def validate_pregunta_id(cls, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError("El ID de la pregunta debe ser un número entero positivo.")
        return value

    @field_validator("respuesta_id")
    def validate_respuesta_id(cls, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError(
                "El ID de la respuesta debe ser un número entero positivo."
            )
        return value


# Modelo para actualizar una respuesta de usuario existente
class RespuestaDeUsuarioUpdate(BaseModel):
    test_id: int = Field(default=1)
    pregunta_id: int = Field(default=1)
    respuesta_id: Optional[int] = Field(default=1)

    @field_validator("test_id")
    def validate_test_id(cls, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError("El ID del test debe ser un número entero positivo.")
        return value

    @field_validator("pregunta_id")
    def validate_pregunta_id(cls, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError("El ID de la pregunta debe ser un número entero positivo.")
        return value

    @field_validator("respuesta_id")
    def validate_respuesta_id(cls, value):
        if value is not None and (not isinstance(value, int) or value < 1):
            raise ValueError(
                "El ID de la respuesta debe ser un número entero positivo."
            )
        return value
