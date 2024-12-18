from sqlalchemy import Column, Integer, String, Date
from datetime import datetime
from .sch_base import Base

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    fecha_creacion = Column(Date, default=datetime.utcnow)
    fecha_actualizacion = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)