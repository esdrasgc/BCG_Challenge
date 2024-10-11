from openai import OpenAI
from typing import List
import os
from dotenv import load_dotenv

def get_openai_client():
    load_dotenv("openai")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=OPENAI_API_KEY)

def generate_embeddings(input: List[str], model='text-embedding-ada-002') -> List[float]:
    client = get_openai_client()
    embedding = client.embeddings.create(
        model=model,
        input=input
    )
    return embedding.data[0].embedding
