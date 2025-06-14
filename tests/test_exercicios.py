import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from app import app
from database.session import get_db
import pytest_asyncio
from unittest import mock


# Configuração do banco de dados de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture para sobrescrever a dependência do banco de dados no FastAPI
@pytest.fixture(name="db_session")
def db_session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest_asyncio.fixture(name="client")
async def client_fixture(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app=app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.mark.asyncio
@mock.patch('utils.ia.gerar_descricao_exercicio')
@mock.patch('utils.ia.gerar_vantagens_exercicio')
async def test_criar_exercicio_automaticamente(mock_gerar_vantagens, mock_gerar_descricao, client):
    # Configura os mocks para retornar valores simulados
    mock_gerar_descricao.return_value = "Descrição simulada do exercício."
    mock_gerar_vantagens.return_value = "Vantagens simuladas do exercício."

    response = client.post("/exercicios/automatico")
    assert response.status_code == 200
    data = response.json()
    assert "nome" in data
    assert "descricao" in data
    assert "vantagens" in data
    assert data["exercicio_ativo"] is True

@pytest.mark.asyncio
@mock.patch('utils.ia.gerar_descricao_exercicio')
@mock.patch('utils.ia.gerar_vantagens_exercicio')
async def test_concluir_exercicio(mock_gerar_vantagens, mock_gerar_descricao, client, db_session):
    # Configura os mocks para a criação inicial
    mock_gerar_descricao.return_value = "Descrição simulada do exercício."
    mock_gerar_vantagens.return_value = "Vantagens simuladas do exercício."

    # Primeiro, crie um exercício para concluir
    create_response = client.post("/exercicios/automatico")
    assert create_response.status_code == 200
    exercicio_criado_id = create_response.json()["id"]

    # Reseta os mocks e configura para a geração do novo exercício (chamado após a conclusão)
    mock_gerar_descricao.reset_mock()
    mock_gerar_vantagens.reset_mock()
    mock_gerar_descricao.return_value = "Nova descrição simulada."
    mock_gerar_vantagens.return_value = "Novas vantagens simuladas."

    response = client.patch(f"/exercicios/concluir/{exercicio_criado_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["msg"] == "Exercício concluído e um novo exercício gerado"
    assert data["exercicio_concluido"] == exercicio_criado_id
    assert "novo_exercicio_gerado" in data
    assert data["novo_exercicio_gerado"] != exercicio_criado_id
