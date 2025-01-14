from sqlalchemy import Column, Integer, String
from .sch_base import Base

class Recurso(Base):
    __tablename__ = "recursos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    autor = Column(String, nullable=True)
    plataforma = Column(String, nullable=True)
    enlace = Column(String, nullable=True)