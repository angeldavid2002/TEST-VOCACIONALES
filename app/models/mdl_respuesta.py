from pydantic import BaseModel


class Respuesta(BaseModel):
    id: int
    pregunta_id: int
    respuesta: str
    vocacion: str