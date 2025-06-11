from fastapi import FastAPI
import os
from sqlalchemy import create_engine
from models.base import Base
from models.exercicios import Exercicios
from models.exercicios_ativos import Exercicios_ativos
from models.exercicios_historico import Exercicios_historicos

# Configuração do banco de dados
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "db", "mvp.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Criar as tabelas do banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API de Exercícios"}
