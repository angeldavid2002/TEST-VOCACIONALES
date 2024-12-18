from sqlalchemy import Column, Integer, String
from .base import Base

class Institucion(Base):
    __tablename__ = "instituciones"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
