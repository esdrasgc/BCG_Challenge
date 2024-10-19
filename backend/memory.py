import uuid

from langchain_core.chat_history import InMemoryChatMessageHistory

chat_history = InMemoryChatMessageHistory()
# def generate_session_id():

#     """
#     Generate a unique session ID for tracking user sessions.

#     Returns:
#         dict: A dictionary containing the session ID.
#     """
#     session_id = uuid.uuid4()
#     config = {"configurable": {"session_id": session_id}}
#     return config 

def get_chat_history(session_id: str = None) -> InMemoryChatMessageHistory:
    return chat_history

def clear_chat_history() -> None:
    chat_history.clear()
