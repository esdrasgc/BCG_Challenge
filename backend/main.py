from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import openai
import uvicorn
from dotenv import load_dotenv
from uuid import UUID, uuid4


import os
import sys
# Adicionar o diretório raiz do projeto ao sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import graph

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key
client = openai.OpenAI(api_key=openai_api_key)
embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')

app = FastAPI()
app_graph = graph.graph_init()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=['*'],
#     allow_credentials=False,
#     allow_methods=['*'],
#     allow_headers=['*'],
# )

# Modelos de requisição e resposta
class QueryRequest(BaseModel):
    query: str
    session_id: str = None  # Opcional

class ResponseModel(BaseModel):
    response: str
    session_id: str  # Retorna o session_id

app = FastAPI()

# Inicializar o grafo de estado
state_graph = graph.graph_init()

class QueryRequest(BaseModel):
    session_id: UUID | None = None
    query: str

class QueryResponse(BaseModel):
    session_id: UUID
    response: str

@app.post("/chat", response_model=QueryResponse)
def chat_endpoint(request: QueryRequest):
    if request.session_id is None:
        request.session_id = uuid4()
    config = {"configurable": {"session_id": request.session_id}}
    response = ""
    for output in state_graph.stream({"query": request.query}, config, stream_mode="updates"):
        for node, updates in output.items():
            print(f"Node '{node}': {updates}")
    # Supondo que o estado final contém a chave 'generation'
    response = updates['generation']
    return QueryResponse(response=response, session_id=request.session_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)