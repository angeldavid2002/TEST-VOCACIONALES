from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .sch_base import Base

class Pregunta(Base):
    __tablename__ = "preguntas"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    enunciado = Column(String, nullable=False)

    test = relationship("Test",backref="preguntas")
    