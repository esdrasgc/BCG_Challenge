import numpy as np
from typing import List
import openai
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import pandas as pd
import db

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = openai_api_key
client = openai.OpenAI(api_key=openai_api_key)
embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')

def embeddings_postgres():
    query_sql = "SELECT content, embedding FROM semanticembeddingfast"
    return db.fetch_data(query_sql)


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
    # Calcular o cosseno da similaridade
    similarity = vec_a.dot(vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    return similarity

def query_toEmbedding(query:str):
  embedding_vector = generate_embeddings(query)
  return embedding_vector

def retriever(query:str, db,  k:int = 4):
  query_embeddings = query_toEmbedding(query = query)
  results = db[[2, 3]] 
  similars = []
  for content, embedding_str in results.values:
      # Convert the embedding string (stored as text in Postgres) back into a list of floats
      embedding_list = [float(x) for x in embedding_str.strip("[]").split(",")]
      
      # Calculate cosine similarity
      similarity = _get_cos(query_embeddings, embedding_list)

      
      # Store the result along with the similarity score
      similars.append((content, similarity))

  # Sort the results by similarity, from highest to lowest
  sorted_similars = sorted(similars, key=lambda x: x[1], reverse=True)

  # Return the top-k results
  return sorted_similars[:k]
    

def retriever_with_score(query: str, db, k: int = 4):
    """
    Performs a search in the Postgres database and returns the most similar documents with their scores.
    """
    # Generate the embedding for the query
    query_embeddings = generate_embeddings(query)

    # Fetch stored embeddings from Postgres
    results = db[[2, 3]]  # Assuming 'content' is the text and 'embedding' is the embedding string

    results_with_scores = []
    for content, embedding_str in results.values:
        # Convert the embedding string (stored as text) back into a list of floats
        embedding_list = [float(x) for x in embedding_str.strip("[]").split(",")]

        # Calculate cosine similarity
        
        similarity = _get_cos(query_embeddings, embedding_list)

        # Store the result along with the similarity score
        results_with_scores.append((content, similarity))

    # Sort the results by similarity, from highest to lowest
    sorted_results = sorted(results_with_scores, key=lambda x: x[1], reverse=True)

    # Return the top-k results
    return sorted_results[:k]
