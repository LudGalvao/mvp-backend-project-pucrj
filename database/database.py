from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Garantir que o diretório db existe
os.makedirs(os.path.dirname(os.path.abspath(__file__)) + "/db", exist_ok=True)

# URL do banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "mvp.db")

# Criando o engine do SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Criando a sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 