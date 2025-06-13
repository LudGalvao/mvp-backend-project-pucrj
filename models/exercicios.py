from sqlalchemy import Column, Integer, String, Index, Boolean
from models.base import Base

class Exercicios(Base):
    __tablename__ = 'exercicios'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(500), nullable=False)
    vantagens = Column(String(500), nullable=False)
    exercicio_ativo = Column(Boolean, nullable=False, default=False)

    # Adicionando índices
    __table_args__ = (
        Index('idx_exercicios_nome', 'nome'),
        Index('idx_exercicios_ativo', 'exercicio_ativo'),
    )

    def __init__(self, nome:str, descricao:str, vantagens:str, exercicio_ativo:bool = False):
        self.nome = nome
        self.descricao = descricao
        self.vantagens = vantagens
        self.exercicio_ativo = exercicio_ativo
