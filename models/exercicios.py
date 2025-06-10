from sqlalchemy import Column, Integer, String
from models.base import Base

class Exercicios(Base):
    __tablename__ = 'exercicios'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(500), nullable=False)
    vantagens = Column(String(500), nullable=False)

    def __init__(self, nome:str, descricao:str, vantagens:str):
        self.nome = nome
        self.descricao = descricao
        self.vantagens = vantagens
