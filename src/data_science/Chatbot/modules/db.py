#Essa parte é temporária, apenas para o código ter alguma rag temporária para testar o bot

import os
import faiss
from typing import List
from langchain_text_splitters import CharacterTextSplitter
import pandas as pd
from langchain_community.vectorstores import FAISS
import utils

def load_file(file_path: str) -> str:
    """Load a text file from a given path."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def embedding_df(file_content, chunk_size: int = 500, chunk_overlap: int = 100) -> pd.DataFrame:
    """Generate a DataFrame with embeddings from a text file."""
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base", chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    docs = text_splitter.split_text(file_content)
    print(f'o documento foi dividido em {len(docs)} chunks')
    df = pd.DataFrame(docs, columns=["content"])
    df["embedding"] = df["content"].apply(lambda x: utils.generate_embeddings([x]))

    return df

def faiss_db(df: pd.DataFrame) -> FAISS:
    """Create a FAISS database from a DataFrame."""
    docs = df["content"].tolist()
    embedding_list = df["embedding"].tolist()
    text_embeddings_pairs = list(zip(docs, embedding_list))

    db = FAISS.from_embeddings(text_embeddings_pairs, embedding_list)
    return db
file_path = r'C:\Users\felip\Programação\Bcg\chatbot\plano-acao-adaptacao-climatica-nacional.txt'
file_content = load_file(file_path)
df = embedding_df(file_content)
database = faiss_db(df)
database.save_local(r"C:\Users\felip\Programação\Bcg\chatbot\modules\faiss_index")