import psycopg2
from psycopg2.extras import execute_values
import os

def connect_to_db():
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'vector_db')
    DB_USER = os.getenv('DB_USER', 'usuario')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'senha')

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None

def criar_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS semanticEmbedding (
                id bigserial primary key, 
                document text,
                content text,
                embedding vector(1536)
            );
            TRUNCATE TABLE semanticEmbedding;
        """)
        conn.commit()
        print("Tabela 'semanticEmbedding' criada ou já existente.")
        
def insert_data(conn, data):
    insert_command = "INSERT INTO semanticEmbedding (document, content, embedding) VALUES %s"
    with conn.cursor() as cur:
        execute_values(cur, insert_command, data)
    conn.commit()
