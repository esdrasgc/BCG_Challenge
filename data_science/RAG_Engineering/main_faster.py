import os
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from dotenv import load_dotenv
import logging
from pathlib import Path

# Setting up the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Function to create the table if it does not already exist
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

# Function to load and insert data into the database
def inserir_dados(conn, csv_file):
    # Load the CSV, ignoring the index
    df = pd.read_csv(csv_file, sep=';', index_col=0)
    
    # Get the file name without extension to use in the 'document' column
    document_name = os.path.splitext(os.path.basename(csv_file))[0]

    # Prepare the data for insertion
    ingestion_data = [(document_name, row['content'], row['embedding']) for _, row in df.iterrows()]
    
    # Insert the data into the database
    insert_command = "INSERT INTO semanticEmbeddingFast (document, content, embedding) VALUES %s"
    
    with conn.cursor() as cur:
        execute_values(cur, insert_command, ingestion_data)
        conn.commit()
    logger.info(f"Dados do arquivo {csv_file} inseridos com sucesso.")

def main():
    # Path to the folder where the embedded files are located
    embedded_files_dir = Path(__file__).parent / 'embedded_files'
    
    # Connect to the database
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
    
    # Create the table if necessary
    criar_tabela(conn)
    


    embedded_files_dir = Path(embedded_files_dir)

    # Process all CSV files in the 'embedded_files' folder
    for csv_file in embedded_files_dir.iterdir():
        if csv_file.suffix == '.csv':
            try:
                inserir_dados(conn, csv_file)
            except Exception as e:
                logger.error(f"Erro ao inserir dados do arquivo {csv_file.name}: {e}")

    
    # Close the connection to the database
    conn.close()
    logger.info("Conexão com o banco de dados fechada.")

if __name__ == '__main__':
    main()
