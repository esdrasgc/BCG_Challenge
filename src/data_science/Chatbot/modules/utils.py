import numpy as np
from typing import List
import openai
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import pandas as pd
import ast

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = openai_api_key
client = openai.OpenAI(api_key=openai_api_key)



def generate_embeddings(input: List[str], client = client, model='text-embedding-ada-002')-> List[float]:
    embedding = client.embeddings.create(
        model=model,
        input=input
    )
    total_tokens = embedding.usage.total_tokens
    embeddings = [data.embedding for data in embedding.data]
    return embedding.data[0].embedding
def _get_cos(vec_a: list, vec_b: list):
    vec_a = np.array(vec_a)
    vec_b = np.array(vec_b)
    return vec_a.dot(vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

def query_toEmbedding(query:str):
  embedding_vector = generate_embeddings(query)
  return embedding_vector
embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')
db = FAISS.load_local(r"C:\Users\felip\Desktop\dab", embeddings, allow_dangerous_deserialization=True)
def retriever(query:str, k:int = 4, db = db):
  query_embeddings = query_toEmbedding(query = query)
  topk = db.similarity_search_by_vector(query_embeddings, k=k)
  return topk

df = pd.read_csv(r'C:\Users\felip\Programação\Bcg\chatbot\faiss.csv')
def retriever_with_score(query:str, df = df, k:int = 4, db = db):
  topk = retriever(query, k, db)
  query_embeddings = query_toEmbedding(query=query)
  scores = []
  #results_with_scores = []
  for doc in topk:
      doc_content = doc.page_content
      matching_row = df[df["content"] == doc_content]  # Supondo que cada documento tenha um campo 'embedding'
      if not matching_row.empty:
            doc_embedding = matching_row.iloc[0]["embedding"]  # Acessa o primeiro resultado
            doc_embedding = ast.literal_eval(doc_embedding)
            query_embeddings = np.array(query_embeddings, dtype=np.float32)
            doc_embedding = np.array(doc_embedding, dtype=np.float32)

            # Calcular a similaridade do cosseno entre o embedding da consulta e o documento
            score = _get_cos(query_embeddings, doc_embedding)
            scores.append(score)
      else:
          print(f"Documento não encontrado no DataFrame: {doc_content}")
      # Adicionar o documento e seu score à lista de resultados
      #results_with_scores.append((doc, score))

  return topk, scores

