from pydantic import BaseModel


class VocacionDeUsuario(BaseModel):
    id: int
    id_usuario: int
    id_test: int
    moda_vocacion: str