import re
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str = Field(default="stringst")
    email: str = Field(default="string@mail.com")
    edad: int = Field(default=1)
    id_ciudad: Optional[int] = Field(default=1)
    id_institucion: Optional[int] = Field(default=1)
    fecha_registro: date = Field(default_factory=date.today)
    password: str = Field(default="stringst")

    @field_validator("edad")
    def validate_age(cls, value):
        if value is not None and value <= 0:
            raise ValueError("La edad debe ser un número entero positivo.")
        return value
    
    @field_validator("nombre")
    def validate_nombre(cls, value):
        if len(value) < 2 or len(value) > 50:
            raise ValueError("El nombre debe tener entre 2 y 50 caracteres.")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        return value

    @field_validator("email")
    def validate_email(cls, value):
        # Expresión regular para validar el formato del correo electrónico
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise ValueError("El correo electrónico proporcionado no es válido. Asegúrate de que tenga el formato correcto.")
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
                raise ValueError("La fecha de registro debe tener el formato YYYY-MM-DD.")
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
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise ValueError("El correo electrónico proporcionado no es válido. Asegúrate de que tenga el formato correcto.")
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