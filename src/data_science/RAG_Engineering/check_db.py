import psycopg2
from psycopg2 import sql
import logging
from dotenv import load_dotenv
import os
import pandas as pd

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do banco de dados
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'vector_db')
DB_USER = os.getenv('DB_USER', 'usuario')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'senha')

# Função para conectar ao banco de dados
def conectar_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info("Conexão bem-sucedida ao banco de dados.")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para listar todas as tabelas no banco de dados
def listar_tabelas(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tabelas = cur.fetchall()
        logger.info("Tabelas no banco de dados:")
        for tabela in tabelas:
            print(tabela[0])

# Função para checar a estrutura da tabela 'semanticEmbedding'
def checar_estrutura_tabela(conn, tabela):
    with conn.cursor() as cur:
        cur.execute(sql.SQL("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s"), [tabela])
        colunas = cur.fetchall()
        logger.info(f"Estrutura da tabela '{tabela}':")
        for coluna in colunas:
            print(f"Coluna: {coluna[0]}, Tipo: {coluna[1]}")

# Função para visualizar as primeiras linhas da tabela 'semanticEmbedding' e formatar como pandas DataFrame
def visualizar_dados(conn, tabela, limite=5):
    with conn.cursor() as cur:
        cur.execute(sql.SQL("SELECT * FROM {} LIMIT %s").format(sql.Identifier(tabela)), [limite])
        colunas = [desc[0] for desc in cur.description]  # Pegando os nomes das colunas
        linhas = cur.fetchall()
        
        # Convertendo os dados em um DataFrame do pandas
        df = pd.DataFrame(linhas, columns=colunas)
        logger.info(f"Exibindo as primeiras {limite} linhas da tabela '{tabela}':")
        print(df.head())  # Mostrando a saída no estilo df.head()

def main():
    # Conectar ao banco de dados
    conn = conectar_db()
    
    if conn:
        # Listar tabelas
        listar_tabelas(conn)

        # Verificar estrutura da tabela semanticEmbedding
        checar_estrutura_tabela(conn, 'semanticembedding')

        # Visualizar os primeiros dados da tabela e exibir no formato pandas
        visualizar_dados(conn, 'semanticembedding', limite=5)

        # Fechar a conexão
        conn.close()
        logger.info("Conexão com o banco de dados fechada.")

if __name__ == '__main__':
    main()
