import logging
import time
import os
import pandas as pd
from chunker import SemanticChunker
from openai_utils import generate_embeddings
from db_utils import connect_to_db, criar_tabela, insert_data

# Configurando o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_file(file_path, chunker, conn):
    # Get the document name (without .txt extension)
    document_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Load the text from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Chunk the text
    chunks = chunker.chunk_text(text)
    
    # Create a DataFrame and generate embeddings for each chunk
    df = pd.DataFrame(chunks, columns=["content"])
    df["embedding"] = df["content"].apply(lambda x: generate_embeddings([x]))
    
    # Save to CSV (one file per document)
    csv_filename = f'{document_name}_embedding.csv'
    df.to_csv(csv_filename, sep=';')
    logger.info(f"Saved embeddings to {csv_filename}")

    # Insert data into the database with the document name
    ingestion_data = [(document_name, row['content'], row['embedding']) for _, row in df.iterrows()]
    insert_data(conn, ingestion_data)

def main():
    start_time = time.time()
    
    # Define the path to the bronze folder
    bronze_folder = r'..\..\..\data\bronze'
    
    # Initialize the SemanticChunker
    chunker = SemanticChunker(threshold=0.75, batch_size=5)
    
    # Connect to the database and create the table if not exists
    conn = connect_to_db()
    if conn:
        criar_tabela(conn)

        # Iterate over all files in the bronze folder
        for filename in os.listdir(bronze_folder):
            file_path = os.path.join(bronze_folder, filename)
            
            if os.path.isfile(file_path) and file_path.endswith('.txt'):  # Process only .txt files
                logger.info(f"Processing file: {filename}")
                process_file(file_path, chunker, conn)

        # Close the connection
        conn.close()
    
    logger.info(f"Total processing time: {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
