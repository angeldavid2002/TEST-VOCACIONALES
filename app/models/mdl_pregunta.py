from pydantic import BaseModel


class Pregunta(BaseModel):
    id: int
    test_id: int
    enunciado: str