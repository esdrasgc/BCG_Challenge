import uuid

from langchain_core.chat_history import InMemoryChatMessageHistory

chats_by_session_id = {}
def generate_session_id():
    session_id = uuid.uuid4()
    config = {"configurable": {"session_id": session_id}}
    return config 

def get_chat_history(session_id: str = None) -> InMemoryChatMessageHistory:
    chat_history = chats_by_session_id.get(session_id)
    if chat_history is None:
        chat_history = InMemoryChatMessageHistory()
        chats_by_session_id[session_id] = chat_history
    return chat_history

def start_new_chat() -> str:
    session_id = generate_session_id()
    chats_by_session_id[session_id] = InMemoryChatMessageHistory()
    return session_id