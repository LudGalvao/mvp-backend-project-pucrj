from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from models.base import Base

class Exercicios_historicos(Base):
    __tablename__ = "exercicios_historicos"

    id = Column(Integer, primary_key = True)
    exercicio_id = Column(Integer, ForeignKey("exercicios.id"), nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    data_conclusao = Column(DateTime, nullable=True)

    def __init__(self, exercicio_id:int, data_inicio: Optional[datetime] = None, data_conclusao: Optional[datetime] = None):
        self.exercicio_id = exercicio_id
        self.data_inicio = data_inicio or datetime.now()
        self.data_conclusao = data_conclusao
