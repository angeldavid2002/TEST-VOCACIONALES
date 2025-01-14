from pydantic import BaseModel
from typing import Optional

class RecursoCreate(BaseModel):
    nombre: str
    tipo: str
    autor: Optional[str] = None
    plataforma: Optional[str] = None
    enlace: Optional[str] = None
