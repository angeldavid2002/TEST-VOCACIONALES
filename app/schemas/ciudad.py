from sqlalchemy import Column, Integer, String, Float
from .base import Base

class Ciudad(Base):
    __tablename__ = "ciudades"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False, unique=True)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
