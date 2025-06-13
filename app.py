from fastapi import FastAPI
from models.base import Base
from config.settings import APP_NAME
from routes import exercicios, exercicios_historico, contador, concluir_exercicios_ativos
from database.session import engine

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
