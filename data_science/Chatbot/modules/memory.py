import uuid

from langchain_core.chat_history import InMemoryChatMessageHistory

chats_by_session_id = {}
def generate_session_id():

    """
    Generate a unique session ID for tracking user sessions.

    Returns:
        dict: A dictionary containing the session ID.
    """
    session_id = uuid.uuid4()
    config = {"configurable": {"session_id": session_id}}
    return config 

def get_chat_history(session_id: str = None) -> InMemoryChatMessageHistory:
    """
    Retrieve or initialize chat history for a given session ID.

    Args:
        session_id (str, optional): The session ID for which to retrieve the chat history.

    Returns:
        InMemoryChatMessageHistory: The chat history for the session.
    """
    
    
    chat_history = chats_by_session_id.get(session_id)
    if chat_history is None:
        chat_history = InMemoryChatMessageHistory()
        chats_by_session_id[session_id] = chat_history
    return chat_history

def start_new_chat() -> str:
    session_id = generate_session_id()
    chats_by_session_id[session_id] = InMemoryChatMessageHistory()
    return session_id