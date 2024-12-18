from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Respuesta(Base):
        __tablename__ = "respuestas"
        id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        pregunta_id = Column(Integer, ForeignKey("preguntas.id"), nullable=False)
        respuesta = Column(String, nullable=False)
        vocacion = Column(String, nullable=False)
        
        pregunta = relationship("Pregunta")
