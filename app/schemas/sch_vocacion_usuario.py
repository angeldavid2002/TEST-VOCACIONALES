from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .sch_base import Base

class VocacionDeUsuarioPorTest(Base):
    __tablename__ = "vocaciones_de_usuario_por_test"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_test = Column(Integer, ForeignKey("tests.id"), nullable=False)
    moda_vocacion = Column(String, nullable=False)

    usuario = relationship("Usuario")
    test = relationship("Test")