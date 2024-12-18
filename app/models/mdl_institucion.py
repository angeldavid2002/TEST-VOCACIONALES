from pydantic import BaseModel


class Institucion(BaseModel):
    id: int
    nombre: str
    direccion: str
    telefono: str