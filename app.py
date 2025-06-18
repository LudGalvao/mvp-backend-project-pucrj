from fastapi import FastAPI
from models.base import Base
from config.settings import APP_NAME
from routes import exercicios, exercicios_historico, contador, concluir_exercicios_ativos
from database.session import engine
from fastapi.middleware.cors import CORSMiddleware

# Criar as tabelas do banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Exercícios",
    description="Documentação da API de Exercícios usando FastAPI e Swagger",
    version="1.0.0"
)

# Adicionar middleware CORS
origins = [
    "http://localhost",
    "http://localhost:8080", # Exemplo, adicione as origens do seu frontend aqui
    "http://127.0.0.1:5500", # Exemplo para Live Server do VS Code
    "*" # Para desenvolvimento, permita todas as origens (não recomendado para produção)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"]
)

app.include_router(exercicios.router)
app.include_router(exercicios_historico.router)
app.include_router(contador.router)
app.include_router(concluir_exercicios_ativos.router)
