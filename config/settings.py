from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "db", "mvp.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

APP_NAME = "API de Exercícios"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
