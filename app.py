from fastapi import FastAPI
from sqlalchemy import create_engine
from models.base import Base
from models.exercicios import Exercicios
from models.exercicios_ativos import Exercicios_ativos
from models.exercicios_historico import Exercicios_historicos
from config.settings import SQLALCHEMY_DATABASE_URL, APP_NAME

# Configuração do banco de dados
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Criar as tabelas do banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title=APP_NAME)

@app.get("/")
def read_root():
    return {"message": APP_NAME}
