from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .sch_base import Base

class RespuestaDeUsuario(Base):
    __tablename__ = "respuestas_de_usuario"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    respuesta_id = Column(Integer, ForeignKey("respuestas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    test = relationship("Test")
    respuesta = relationship("Respuesta")
    usuario = relationship("Usuario")