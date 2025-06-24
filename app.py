from fastapi import FastAPI
from models.base import Base
from config.settings import APP_NAME
from routes import exercicios, exercicios_historico, contador, concluir_exercicios_ativos
from database.session import engine
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager

# Criar as tabelas do banco de dados
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Iniciando aplicação...")
    
    # Preload de exercícios populares em background
    from routes.exercicios import startup_preload
    asyncio.create_task(startup_preload())
    
    print("✅ Aplicação iniciada com sucesso!")
    yield
    
    # Shutdown
    print("🔄 Encerrando aplicação...")
    from utils.ia import cleanup
    await cleanup()
    print("✅ Aplicação encerrada!")

app = FastAPI(
    title="API de Exercícios Otimizada",
    description="API de Exercícios com IA otimizada para alta performance",
    version="2.0.0",
    lifespan=lifespan
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

@app.get("/")
async def root():
    return {
        "message": "API de Exercícios com IA Otimizada",
        "version": "2.0.0",
        "status": "online",
        "features": [
            "Geração de exercícios com IA ultra-rápida",
            "Cache inteligente multicamadas",
            "Pool de conexões otimizado",
            "Preload automático de exercícios populares",
            "Fallbacks para alta disponibilidade"
        ]
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoramento"""
    return {"status": "healthy", "timestamp": "2024-12-24T16:30:00Z"}
