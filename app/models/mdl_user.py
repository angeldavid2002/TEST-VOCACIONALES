from pydantic import BaseModel, Field,EmailStr
from datetime import date
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    contrasena: str
    tipo_usuario: str = Field(default="comun")
    id_ciudad: Optional[int] = None
    id_institucion: Optional[int] = None
    fecha_registro: date = Field(default_factory=date.today)

class UsuarioLogin(BaseModel):
    email: EmailStr
    contrasena: str