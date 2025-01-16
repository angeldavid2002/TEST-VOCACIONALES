from pydantic import BaseModel
from typing import Optional

class InstitucionBase(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None

class InstitucionCreate(InstitucionBase):
    nombre: str
    direccion: str
    telefono: str

class InstitucionUpdate(InstitucionBase):
    pass
