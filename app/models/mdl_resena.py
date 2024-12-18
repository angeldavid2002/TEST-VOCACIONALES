from datetime import date
from typing import Optional
from pydantic import BaseModel


class ResenaBase(BaseModel):
    id: int
    id_usuario: int
    comentario: str
    puntuacion: int
    fecha_creacion: Optional[date] = None