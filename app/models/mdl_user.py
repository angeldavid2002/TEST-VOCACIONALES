from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import date
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50, description="El nombre debe tener entre 2 y 50 caracteres.")
    email: EmailStr
    password: str = Field(..., min_length=8, description="La contraseña debe tener al menos 8 caracteres.")
    id_ciudad: Optional[int] = None
    id_institucion: Optional[int] = None
    fecha_registro: date = Field(default_factory=date.today)

    @field_validator("id_ciudad", "id_institucion")
    def validate_ids(cls, value):
        if value is not None and value <= 0:
            raise ValueError("El ID debe ser un número entero positivo.")
        return value

    @field_validator("fecha_registro")
    def validate_fecha_registro(cls, value):
        if isinstance(value, str):
            try:
                value = date.fromisoformat(value)
            except ValueError:
                raise ValueError("La fecha de registro debe tener el formato YYYY-MM-DD.")
        return value

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="La contraseña debe tener al menos 8 caracteres.")
    