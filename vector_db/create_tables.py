import os
import psycopg2
from psycopg2 import sql

# Configurações de conexão
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'vector_db')
DB_USER = os.getenv('DB_USER', 'usuario')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'senha')

def criar_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documentos (
                id INTEGER PRIMARY KEY,
                titulo TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                vetor VECTOR(384)  -- Ajuste o tamanho conforme o modelo utilizado
            );
        """)
        conn.commit()
    print("Tabela 'documentos' criada ou já existente.")


def main():
    # Conecta ao banco de dados
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        return


    criar_tabela(conn)


if __name__ == '__main__':
    main()