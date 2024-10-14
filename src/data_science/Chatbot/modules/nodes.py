from langchain.prompts import (ChatPromptTemplate)
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.output_parsers import StrOutputParser
import llm
import utils
import memory 
from langchain_community.utilities import SearxSearchWrapper
import os 
import getpass
from pydantic import BaseModel, Field
import db
import pandas as pd
import edges

model = llm.model_init()
db_total = db.fetch_all_data()
db_total = pd.DataFrame(db_total)
db_small = db_total[db_total[1] == 'itabirito_embedding']
db_medium = db_total[(db_total[1] == 'curitiba_embedding') | (db_total[1] == 'joao_pessoa_embedding')]
db_big = db_total[db_total[1] == 'sao_paulo_embedding']
db_total = db_total[(db_total[1] == 'enfrentamento_embedding') | 
                    (db_total[1] == 'agro_embedding') | 
                    (db_total[1] == 'federal_embedding') | 
                    (db_total[1] == 'nacional_embedding')]

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


def treshhold_docs(query: str, db, treshold:float = 0.5):
  results = utils.retriever_with_score(query, db)
  topk = []
  for doc, score in results:
    if score >= treshold:
        topk.append(doc)

  return topk

class City_name(BaseModel):
    """return the city name"""

    city: str = Field(
        description="Just the name of the city in a query"
    )


### Nodes functions:
def decider(state):
    """
    Route the query to the appropriate source without altering the state.

    Args:
        state (dict): The current graph state, containing at least a query.

    Returns:
        state (dict): Unchanged state
    """
    print("---DECIDER---")
    query = state["query"]
    source = edges.router_func(query)
    choice = source.datasource
    return {"query": query, "choice": choice}

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
    
    choice = state["choice"]
    docs = None
    # Retrieval
    if choice == "general":
      docs = utils.retriever(query, db_total, k=4)

    elif choice == "small_city":
      docs1 = utils.retriever(query, db_small, k=2)
      docs2 = utils.retriever(query, db_total, k=2)

    elif choice == "medium_city":
      docs1 = utils.retriever(query, db_medium, k=2)
      docs2 = utils.retriever(query, db_total, k=2)

    elif choice == "big_city":
      docs1 = utils.retriever(query, db_big, k=2)
      docs2 = utils.retriever(query, db_total, k=2)


    if docs is None:
        context1 = [doc[0] for doc in docs1]  # Extracting the content from (content, similarity)
        context2 = [doc[0] for doc in docs2]
        context = context1 + context2
    else:
        context = [doc[0] for doc in docs]  # Extracting content when only one retrieval is performed


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
    messages = state.get("messages", [])
    chat_history = memory.get_chat_history()   #possível problema aqui
    if messages == " ":
      messages = list(chat_history.messages)
    else:
      messages = list(chat_history.messages) + messages
    generation = llm.call_llm(query = query, context = context, memory = messages)
    chat_history.add_user_message(query)
    chat_history.add_ai_message(generation)  #Ver se isso não gera repetições e se adiciona certo
    state["messages"] = messages
    if messages == []:
      print("messages is empty")
    return {"context": context, "query": query, "generation": generation, "messages": messages}


def same(state):
  print("---SAME---")
  query = state["query"]

  return {"query": query}

def first_prompt(state):

  print("---SAME---")
  query = state["query"]

  return {"query": query}



def city_node(state):
  query = state["query"]
  #messages = state.get("messages", " ")  Coloco isso na memória?
  structured_llm_grader = model.with_structured_output(City_name)
  system = """You are a geography specialist who knows very well city names. In a query in which there is a city name for sure, just return this city name."""
  city_prompt = ChatPromptTemplate.from_messages(
      [
          ("system", system),
          ("human", "User query: {query}"),
      ]
  )
  name = city_prompt | structured_llm_grader
  response = name.invoke({"query": query})
  response = response.city
  climate_query = f"Aspectos climáticos de {response}"
  docs = search_tool(climate_query)
  climate_system = """You are a climate specialist who is well-acquainted with the climatic characteristics of cities.
  Given a city name, provide general climatic characteristics of that city and the problems it faces related to those aspects."""
  #Fazer um prompt aqui que retorne mais estruturadamente as informações.

  climate_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", climate_system),
        ("human", "the city I want to know about the climate problems and climate characteristics is {response}, here is context: {docs}"),
    ]
  )
  climate_chain = climate_prompt | model
  climate_response = climate_chain.invoke({"response": response, "docs": docs})
  print(climate_response.content)
  return {"query": query}   #Será que adiciono isso na memória ou algo do tipo?


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

def treshold_check(state, treshold:float = 0.5):
  """
  Check the document scores and filter them based on a threshold.

  Args:
      state (dict): The current graph state containing query and threshold.

  Returns:
      state (dict): Updates 'top_docs' key with documents that passed the threshold.
  """

  print("---THRESHOLD CHECK---")
  query = state["query"]
  choice = state["choice"]

  # Get top documents based on threshold
  if choice == "general":
    top_docs = treshhold_docs(query, db_total, treshold)
  
  elif choice == "small_city":
    top_docs1 = treshhold_docs(query, db_small, treshold)
    top_docs2 = treshhold_docs(query, db_total, treshold)
    top_docs = top_docs1 + top_docs2  # Combine results from both databases

  elif choice == "medium_city":
    top_docs1 = treshhold_docs(query, db_medium, treshold)
    top_docs2 = treshhold_docs(query, db_total, treshold)
    top_docs = top_docs1 + top_docs2  # Combine results from both databases

  elif choice == "big_city":
    top_docs1 = treshhold_docs(query, db_big, treshold)
    top_docs2 = treshhold_docs(query, db_total, treshold)
    top_docs = top_docs1 + top_docs2  # Combine results from both databases

  else:
    top_docs = []
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