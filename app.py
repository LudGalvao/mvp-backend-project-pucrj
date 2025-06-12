from fastapi import FastAPI
from sqlalchemy import create_engine
from models.base import Base
from config.settings import SQLALCHEMY_DATABASE_URL, APP_NAME
from routes import exercicios, exercicios_historico, contador, concluir_exercicios_ativos

# Configuração do banco de dados
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Criar as tabelas do banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Exercícios",
    description="Documentação da API de Exercícios usando FastAPI e Swagger",
    version="1.0.0"
)

app.include_router(exercicios.router)
app.include_router(exercicios_historico.router)
app.include_router(contador.router)
app.include_router(concluir_exercicios_ativos.router)

@app.get("/")
def read_root():
    return {"message": APP_NAME}
