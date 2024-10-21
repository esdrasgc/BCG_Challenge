import os
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from dotenv import load_dotenv
import logging
from pathlib import Path

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do banco de dados
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Função para criar a tabela se ela ainda não existir
def criar_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS semanticEmbeddingFast (
                id bigserial primary key, 
                document text,
                content text,
                embedding vector(1536) -- Verificar o tamanho do vetor conforme o modelo usado
            );
        """)
        conn.commit()
    logger.info("Tabela 'semanticEmbeddingFast' criada ou já existente.")

# Função para carregar e inserir dados no banco de dados
def inserir_dados(conn, csv_file):
    # Carregar o CSV, ignorando o índice
    df = pd.read_csv(csv_file, sep=';', index_col=0)
    
    # Obter o nome do arquivo sem extensão para usar na coluna 'document'
    document_name = os.path.splitext(os.path.basename(csv_file))[0]

    # Preparar os dados para inserção
    ingestion_data = [(document_name, row['content'], row['embedding']) for _, row in df.iterrows()]
    
    # Inserir os dados no banco
    insert_command = "INSERT INTO semanticEmbeddingFast (document, content, embedding) VALUES %s"
    
    with conn.cursor() as cur:
        execute_values(cur, insert_command, ingestion_data)
        conn.commit()
    logger.info(f"Dados do arquivo {csv_file} inseridos com sucesso.")

def main():
    # Caminho da pasta onde os arquivos embedados estão

    embedded_files_dir = Path(__file__).parent / 'embedded_files'
    
    # Conectar ao banco de dados
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        return
    
    # Criar a tabela, se necessário
    criar_tabela(conn)
    


    embedded_files_dir = Path(embedded_files_dir)

    # Processar todos os arquivos CSV da pasta 'embedded_files'
    for csv_file in embedded_files_dir.iterdir():
        if csv_file.suffix == '.csv':
            try:
                inserir_dados(conn, csv_file)
            except Exception as e:
                logger.error(f"Erro ao inserir dados do arquivo {csv_file.name}: {e}")

    
    # Fechar a conexão com o banco de dados
    conn.close()
    logger.info("Conexão com o banco de dados fechada.")

if __name__ == '__main__':
    main()
