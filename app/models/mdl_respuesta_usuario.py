from pydantic import BaseModel


class RespuestaDeUsuario(BaseModel):
    id: int
    test_id: int
    respuesta_id: int
    usuario_id: int