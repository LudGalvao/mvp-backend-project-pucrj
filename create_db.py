import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configuração do banco de dados
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "db", "mvp.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Importando os modelos
from models.base import Base
from models.exercicios import Exercicios
from models.exercicios_ativos import Exercicios_ativos
from models.exercicios_historico import Exercicios_historicos

def init_db():
    print("Criando as tabelas do banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    init_db() 