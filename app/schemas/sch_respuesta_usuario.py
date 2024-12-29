from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .sch_base import Base

class RespuestaDeUsuario(Base):
    __tablename__ = "respuestas_de_usuario"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    pregunta_id = Column(Integer, ForeignKey("preguntas.id"), nullable=False)
    respuesta_id = Column(Integer, ForeignKey("respuestas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    pregunta = relationship("Pregunta",backref="respuestas_de_usuario")
    test = relationship("Test",backref="respuestas_de_usuario")
    respuesta = relationship("Respuesta",backref="respuestas_de_usuario")
    usuario = relationship("Usuario",backref="respuestas_de_usuario")