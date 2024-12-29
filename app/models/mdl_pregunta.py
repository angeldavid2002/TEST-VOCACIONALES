from pydantic import BaseModel, Field, field_validator


class Pregunta(BaseModel):
    id: int
    test_id: int
    enunciado: str

class PreguntaCreate(BaseModel):
    test_id: int = Field(default=1)
    enunciado: str

    @field_validator("test_id")
    def validate_test_id(cls, value):
        if not isinstance(value, int):
            raise ValueError("el id debe ser un número entero.")
        return value

    @field_validator("enunciado")
    def validate_enunciado(cls, value):
        if not isinstance(value, str):
            raise ValueError("El comentario debe ser un texto válido.")
        if len(value) < 5:
            raise ValueError("El comentario debe tener al menos 5 caracteres.")
        if len(value) > 800:
            raise ValueError("El comentario no puede exceder los 800 caracteres.")
        return value

class PreguntaUpdate(BaseModel):
    pregunta_id: int
    enunciado: str

    @field_validator("pregunta_id")
    def validate_pregunta_id(cls, value):
        if not isinstance(value, int):
            raise ValueError("el id debe ser un número entero.")
        return value

    @field_validator("enunciado")
    def validate_enunciado(cls, value):
        if not isinstance(value, str):
            raise ValueError("El comentario debe ser un texto válido.")
        if len(value) < 5:
            raise ValueError("El comentario debe tener al menos 5 caracteres.")
        if len(value) > 800:
            raise ValueError("El comentario no puede exceder los 800 caracteres.")
        return value