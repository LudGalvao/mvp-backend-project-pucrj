from database.init_db import init_db

if __name__ == "__main__":
    print("Criando as tabelas do banco de dados...")
    init_db()
    print("Tabelas criadas com sucesso!") 