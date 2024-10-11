import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from openai import OpenAI
from dotenv import load_dotenv

import os

import nltk
nltk.download('punkt_tab')

from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import NLTKTextSplitter
from tqdm import tqdm
import re
from typing import List
import pandas as pd
import logging
import time


#db
import os
import psycopg2
from psycopg2.extras import execute_values
# Configurando o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
"""
with open(r'..\..\..\data\bronze\nacional.txt', 'r',encoding='utf-8') as file:
    text = file.read()

# Now, file_content contains the entire content of the text file
print(text)
print('##################################################')


class SemanticChunker:
    def __init__(self, model_name='distilbert-base-uncased', threshold=0.8, batch_size=5):
        # Usando o modelo DistilBERT, que é mais leve em memória
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.threshold = threshold
        self.batch_size = batch_size

    def get_embeddings(self, sentences):
        # Truncamento para evitar processamento de sequências muito grandes
        inputs = self.tokenizer(sentences, return_tensors='pt', padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        # Extraindo a média das representações dos tokens
        return outputs.last_hidden_state.mean(dim=1).numpy()
    
    def chunk_text(self, text):
        sentences = text.split('. ')
        chunks = []
        
        # Processando as sentenças em lotes para reduzir o consumo de memória
        for i in range(0, len(sentences), self.batch_size):
            batch_sentences = sentences[i:i+self.batch_size]
            embeddings = self.get_embeddings(batch_sentences)

            current_chunk = [batch_sentences[0]]
            for j in range(1, len(batch_sentences)):
                similarity = cosine_similarity([embeddings[j-1]], [embeddings[j]])[0][0]
                if similarity < self.threshold:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [batch_sentences[j]]
                else:
                    current_chunk.append(batch_sentences[j])
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))

        return chunks
# Medindo o tempo total
start_time = time.time()
# Exemplo de uso
chunker = SemanticChunker(threshold=0.75, batch_size=5)

chunks = chunker.chunk_text(text)

# Log do tempo total de execução
logger.info(f"Total processing time create chunks: {time.time() - start_time:.2f} seconds.")

#for i, chunk in enumerate(chunks):
#    print(f"Chunk {i+1}:\n{chunk}\n")

print(f"Chunk {1}:\n{chunks[1]}\n")



load_dotenv("openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_embeddings(input: List[str], model='text-embedding-ada-002')-> List[float]:
    embedding = client.embeddings.create(
        model=model,
        input=input
    )
    total_tokens = embedding.usage.total_tokens
    embeddings = [data.embedding for data in embedding.data]
    return embedding.data[0].embedding

def generate_embeddings(input: List[str],model='text-embedding-ada-002')-> List[float]:
    embedding = client.embeddings.create(
        model=model,
        input=input
    )
    total_tokens = embedding.usage.total_tokens
    embeddings = [data.embedding for data in embedding.data]
    return embedding.data[0].embedding

df = pd.DataFrame(chunks, columns=["content"])
df["embedding"] = df["content"].apply(lambda x: generate_embeddings([x]))

logger.info(f"Total processing time embedd: {time.time() - start_time:.2f} seconds.")
df.to_csv('nacional_embedding.csv',sep=';')

logger.info(f"Total processing save csv: {time.time() - start_time:.2f} seconds.")

print(df.head()) """



df = pd.read_csv('nacional_embedding.csv',sep=';')
print(df.head())


#############################################################################################
#Loading the database
#############################################################################################

# Configurações de conexão
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'vector_db')
DB_USER = os.getenv('DB_USER', 'usuario')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'senha')

def criar_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS semanticEmbedding (
                id bigserial primary key, 
                document text,
                content text,
                embedding vector(1536) --Verificar tamanho do vetor
                );
                TRUNCATE TABLE embeddings;
        """)
        conn.commit()
    print("Tabela 'documentos' criada ou já existente.")

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


criar_tabela(conn)

# Prepare the data for insertion
ingestion_data = [('nacional',row['content'], row['embedding']) for _, row in df.iterrows()]

# Insert the data into the table
insert_command = "INSERT INTO semanticEmbedding (document,content, embedding) VALUES %s"

conn.autocommit = True
cur = conn.cursor()
execute_values(cur, insert_command, ingestion_data)