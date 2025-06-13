from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config.settings import SQLALCHEMY_DATABASE_URL

# Configuração do engine com pool de conexões
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,  # Verifica conexões antes de usar
    pool_recycle=3600,   # Recicla conexões após 1 hora
    pool_size=5,         # Número máximo de conexões
    max_overflow=10      # Número máximo de conexões extras
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()