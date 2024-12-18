from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    contrasena = Column(String, nullable=False)
    tipo_usuario = Column(String, nullable=False)
    id_ciudad = Column(Integer, ForeignKey("ciudades.id"), nullable=True)
    id_institucion = Column(Integer, ForeignKey("instituciones.id"), nullable=True)
    fecha_registro = Column(Date, default=datetime.now(timezone.utc))

    ciudad = relationship("Ciudad")
    institucion = relationship("Institucion")
