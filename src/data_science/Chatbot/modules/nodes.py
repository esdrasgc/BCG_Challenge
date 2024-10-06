from langchain.prompts import (ChatPromptTemplate)
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.output_parsers import StrOutputParser
import llm
import utils
import memory 

model = llm.model_init()


### Nodes functions:

def search_tool(query:str):
  web_search_tool = DuckDuckGoSearchRun()
  return web_search_tool.invoke(query)


def query_rewriter(query:str):
  system = """You a question re-writer that converts an input question to a better version that is optimized \n
      for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
  re_write_prompt = ChatPromptTemplate.from_messages(
      [
          ("system", system),
          (
              "human",
              "Here is the initial query: \n\n {query} \n Formulate an improved question.",
          ),
      ]
  )

  question_rewriter = re_write_prompt | model | StrOutputParser()
  return question_rewriter.invoke({"query": query})


def treshhold_docs(query: str, treshold:float = 0.8):
  topk, scores = utils.retriever_with_score(query)
  for i in range(len(scores)):
    if scores[i] < treshold:
      topk[i] = ' '
  while ' ' in topk:
    topk.remove(' ')
  return topk

### Nodes functions:

def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    query = state["query"]

    # Retrieval
    docs = utils.retriever(query)
    context = [doc.page_content for doc in docs]
    return {"context": context, "query": query}

def generate(state, config = None):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    query = state["query"]
    context = state.get("context", " ")
    messages = state.get("messages", " ")
    chat_history = memory.get_chat_history()   #possível problema aqui
    if messages == " ":
      messages = list(chat_history.messages)
    else:
      messages = list(chat_history.messages) + messages
    generation = llm.call_llm(query = query, context = context, memory = messages)
    chat_history.add_user_message(query)
    chat_history.add_ai_message(generation)  #Ver se isso não gera repetições e se adiciona certo
    return {"context": context, "query": query, "generation": generation, "messages": messages}


def same(state):

    print("---SAME---")
    query = state["query"]

    return {"query": query}


def transform_query(state):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    query = state["query"]
    context = state["context"]

    # Re-write question
    better_query = query_rewriter(query)
    return {"context": context, "query": better_query}

def treshhold_check(state, treshold:float = 0.8):
    """
    Check the document scores and filter them based on a threshold.

    Args:
        state (dict): The current graph state containing query and threshold.

    Returns:
        state (dict): Updates 'top_docs' key with documents that passed the threshold.
    """

    print("---THRESHOLD CHECK---")
    query = state["query"]

    # Get top documents based on threshold
    top_docs = treshhold_docs(query, treshold)

    return {"query": query, "context": top_docs}

def web_search(state):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    print("---WEB SEARCH---")
    query = state["query"]

    # Web search
    web_results = search_tool(query)

    return {"context": web_results, "query": query}