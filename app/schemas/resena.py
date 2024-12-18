from sqlalchemy import Column, Integer, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Resena(Base):
    __tablename__ = "resenas"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    comentario = Column(Text, nullable=False)
    puntuacion = Column(Integer, nullable=False)
    fecha_creacion = Column(Date, default=datetime.utcnow)

    usuario = relationship("Usuario")