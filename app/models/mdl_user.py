import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional


class UsuarioCreate(BaseModel):
    nombre: str = Field(default="stringst")
    email: str = Field(default="string@mail.com")
    sexo: Optional[str] = Field(default="Masculino")  # Masculino - Femenino
    id_ciudad: Optional[int] = Field(default=1)
    id_institucion: Optional[int] = Field(default=1)
    fecha_registro: date = Field(default_factory=date.today)
    password: str = Field(default="stringst")

    # Validación de los campos (sin renombrar a "username")
    @field_validator("nombre")  # Ahora validamos "nombre"
    def validate_nombre(cls, value):
        if len(value) < 2 or len(value) > 50:
            raise ValueError("El nombre debe tener entre 2 y 50 caracteres.")
        return value

    @field_validator("sexo")
    def validate_sexo(cls, value):
        if value not in ["Masculino", "Femenino"]:
            raise ValueError("El sexo debe ser 'Masculino' o 'Femenino'.")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        return value

    @field_validator("email")
    def validate_email(cls, value):
        # Expresión regular para validar el formato del correo electrónico
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, value):
            raise ValueError(
                "El correo electrónico proporcionado no es válido. Asegúrate de que tenga el formato correcto."
            )
        return value

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
                raise ValueError(
                    "La fecha de registro debe tener el formato YYYY-MM-DD."
                )
        return value


class UsuarioLogin(BaseModel):
    email: str = Field(default="string@mail.com")
    password: str = Field(default="stringst")

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        return value

    @field_validator("email")
    def validate_email(cls, value):
        # Expresión regular para validar el formato del correo electrónico
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, value):
            raise ValueError(
                "El correo electrónico proporcionado no es válido. Asegúrate de que tenga el formato correcto."
            )
        return value


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("current_password")
    def validate_current_password(cls, value):
        if len(value) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        return value

    @field_validator("new_password")
    def validate_new_password(cls, value):
        if len(value) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        return value

    @field_validator("confirm_password")
    def validate_confirm_password(cls, value):
        if len(value) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        return value


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(default="stringst")
    sexo: Optional[str] = None
    id_ciudad: Optional[int] = None
    id_institucion: Optional[int] = None

    @field_validator("nombre")
    def validate_nombre(cls, value):
        if len(value) < 2 or len(value) > 50:
            raise ValueError("El nombre debe tener entre 2 y 50 caracteres.")
        return value

    @field_validator("sexo")
    def validate_sexo(cls, value):
        if value not in ["Masculino", "Femenino"]:
            raise ValueError("El sexo debe ser 'Masculino' o 'Femenino'.")
        return value

    @field_validator("id_ciudad", "id_institucion")
    def validate_ids(cls, value):
        if value is not None and value <= 0:
            raise ValueError("El ID debe ser un número entero positivo.")
        return value

class RecoverPasswordRequest(BaseModel):
    email: EmailStr