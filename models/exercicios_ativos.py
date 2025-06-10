from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime ,Column, ForeignKey, Integer
from models.base import Base

class Exercicios_ativos(Base):
    __tablename__= "exercicios_ativos"

    id = Column(Integer, primary_key = True)
    exercicio_id = Column(Integer, ForeignKey("exercicios.id"), nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    concluido = Column(Boolean, nullable=False)
    data_conclusao = Column(DateTime, nullable=True)

    def __init__(self, exercicio_id:int, data_inicio: Optional[datetime] = None, concluido:bool = False,
                  data_conclusao: Optional[datetime] = None):
        self.exercicio_id = exercicio_id
        self.data_inicio = data_inicio or datetime.now()
        self.concluido = concluido
        self.data_conclusao = data_conclusao
