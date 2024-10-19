from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import openai
import uvicorn
from dotenv import load_dotenv
from uuid import UUID, uuid4
from db import create_db_and_tables, get_session
from sqlmodel import Session, select
import os
import graph
from api_models import *

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key
client = openai.OpenAI(api_key=openai_api_key)
embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')

app = FastAPI()
app_graph = graph.graph_init()

# Modelos de requisição e resposta
class QueryRequest(BaseModel):
    query: str
    session_id: str = None  # Opcional

class ResponseModel(BaseModel):
    response: str
    session_id: str  # Retorna o session_id

app = FastAPI()

# Define allowed origins
origins = [
    "http://localhost:3000",  # React default port
    # Add other origins if necessary
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
# Inicializar o grafo de estado
state_graph = graph.graph_init()

@app.get("/chat", response_model=ChatListingResponse)
def list_chats(session: Session = Depends(get_session)):
    chats = session.exec(select(ChatInDB)).all()
    return ChatListingResponse(chats=[chat.to_listing() for chat in chats])

@app.post("/chat", response_model=InitChatResponse)
def new_chat(request: InitChatRequest, session: Session = Depends(get_session)):
    session_id = uuid4()
    config = {"configurable": {"session_id": session_id}}
    response = ""
    prompt_inicial = f'Olá, sou gestor da cidade {request.city.name}-{request.state.abbreviation}.'
    for output in state_graph.stream({"query": prompt_inicial}, config, stream_mode="updates"):
        for node, updates in output.items():
            print(f"Node '{node}': {updates}")

    chat = ChatInDB(
        id=uuid4(),
        city=request.city.name,
        state=request.state.abbreviation,
        session_id=session_id,
        messages=[],
        key_indicators=[]
    )
    session.add(chat)
    session.commit()
    session.refresh(chat)

    # Initialize key indicators (dummy data for now)
    # Replace this with actual key indicators from your `updates`
    key_indicators = [
        KeyIndicatorsInDB(
            id=uuid4(),
            value=1.0,  # Replace with actual value
            name="Sample KPI",
            detail="Detail about Sample KPI",
            chat_id=chat.id
        )
    ]
    session.add_all(key_indicators)
    session.commit()

    return InitChatResponse(
        session_id=session_id,
        id=chat.id,
        city=chat.city,
        state=chat.state
    )


@app.get("/chat/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: UUID, session: Session = Depends(get_session)):
    chat = session.get(ChatInDB, chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat.to_response()

@app.post("/message", response_model=MessageResponse)
def new_message(request: MessageRequest, session: Session = Depends(get_session)):
    chat = session.get(ChatInDB, request.chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    ## save user message in db
    user_message = MessageInDB(
        id = uuid4(),
        chat_id = chat.id,
        content= request.query,
        is_user=True,
    )
    session.add(user_message)
    session.commit()

    config = {"configurable": {"session_id": chat.session_id}}
    response = ""
    for output in state_graph.stream({"query": request.query}, config, stream_mode="updates"):
        for node, updates in output.items():
            print(f"Node '{node}': {updates}")
    # Supondo que o estado final contém a chave 'generation'
    response = updates['generation']
    ## save bot message in db
    bot_message = MessageInDB(
        id = uuid4(),
        chat_id = chat.id,
        content= response,
        is_user=False,
    )
    session.add(bot_message)
    session.commit()
    session.refresh(bot_message)
    return bot_message.to_response()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)