from datetime import date
from typing import Optional
from pydantic import BaseModel


class Test(BaseModel):
    id: int
    nombre: str
    descripcion: str
    fecha_creacion: Optional[date] = None
    fecha_actualizacion: Optional[date] = None