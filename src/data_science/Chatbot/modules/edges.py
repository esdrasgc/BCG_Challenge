from typing import Literal
from pydantic import BaseModel, Field
from langchain.prompts import (
    ChatPromptTemplate
)
import llm
import utils
import memory

model = llm.model_init()

### Edges functions:

    ###Router
class InitialChoice(BaseModel):
    """Route a user query based on the presence and size of the city."""
    
    datasource: Literal["web_search", "general", "small_city", "medium_city", "big_city"] = Field(
        ...,
        description="Route to web search, general vectorstore, or general vectorstore plus other based on the city size",
    )


def router_func(query:str):
  """
  Route a user query to the appropriate path based on the content of the query.
  
  args:
    query (str): The user input.

    Returns:
        str: the llm decision ("web_search", "general", "small_city", "medium_city", "big_city").
  """
  
  
  system = """You are an expert at routing a user question to diferent paths. You have five paths, the web-search, the general vectorstore, the general vectorstore plus a vectorstore of a small city, the general vectorstore plus a vectorstore of a medium city, the general vectorstore plus a vectorstore of a big city.
  The vectorstore contains documents in portuguese related to climate plans for cities in Brazil.
  So if the query is related to the topic use the vectorstore, if some city is mentioned in the query, clasify the message based on the city size. Otherwise, use web-search.
  Just return your chosen path based on the query as the output. Give the output in lowercase."""
  route_prompt = ChatPromptTemplate.from_messages(
      [
          ("system", system),
          ("human", "{query}"),
      ]
  )
  structured_model_router = model.with_structured_output(InitialChoice) #Will return or "vectorstore" or "web_search"
  question_router = route_prompt | structured_model_router
  return question_router.invoke({'query': query})

    ###Tell if a search is needed
class Search_need(BaseModel):
    """Binary score for tell the necessity of web search."""

    binary_score: str = Field(
        description="Is necessary to do a web search on the query, 'yes' or 'no'"
    )


def need_of_search(query:str):
  """ 
    Determine if a web search is necessary based on the user query.
  
    Args:
        query (str): The user input.
    
    Returns:
        str: Binary score for tell the necessity of web search.

  """

  structured_model_needs = model.with_structured_output(Search_need)

  # Prompt
  system = """You are an assistant responsible for determining whether a web search is necessary based on a user's query.
  You will receive a query and must decide if a web search is required. Provide a binary answer: 'yes' if the query cannot be answered without external information, or 'no' if it can be answered with available knowledge.
  Remember that is a continuos chat, so the user can use references that the final assistant will know
  Use your internal knowledge to answer straightforward questions and only suggest a search when it is absolutely necessary.
  Your response format should strictly follow this structure:
  - binary_score: 'yes' or 'no'

  Do not provide any other information or explanations. Respond in lowercase."""

  need_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: {query}"),
    ]
  )
  needs_chain = need_prompt | structured_model_needs
  return needs_chain.invoke({"query": query})


    ###Tell if a city is mentioned
class Has_City(BaseModel):
    """Binary score saying if the prompt has any city"""

    binary_score: str = Field(
        description="Does this query mention a city anywhere in the world, 'Yes' or 'No'"
    )

def Hascity_func(query:str):
    '''
    Determine if a city is mentioned in the user query.

    Args:
        query (str): The user input.
    
    Returns:
        str: Binary score saying if the prompt has any city.
    '''

    structured_llm_grader = model.with_structured_output(Has_City)

  # Prompt
    system = """You are a geography specialist who knows very well city names. Give a binary score 'yes' or 'no' score to indicate whether the user query mention any city in the world. Responds in lowercase."""
    city_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "User query: {query}"),
        ]
    )
    retrieval_grader = city_prompt | structured_llm_grader

    response = retrieval_grader.invoke({"query": query})
    return response




### Edges:

def route_question(state):
    """
    Route question to web search or the type of RAG to use.

    Args:
        state (dict): The current graph state

    Returns:
        str: the path to follow ("web_search", "general", "small_city", "medium_city", "big_city").
    """

    print("---ROUTE QUESTION---")
    choice = state["choice"] 
    if choice == "web_search":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "Need" 
    elif choice == "general":
        print("---ROUTE QUESTION TO GENERAL RAG---")
        return "general"
    elif choice == "small_city":
        print("---ROUTE QUESTION TO RAG + SMALL CITY---")
        return "small_city"
    elif choice == "medium_city":
        print("---ROUTE QUESTION TO RAG + MEDIUM CITY---")
        return "medium_city"
    elif choice == "big_city":
        print("---ROUTE QUESTION TO RAG + BIG CITY---")
        return "big_city"
    
def DoSearch(state):
    """
    Determine if a web search is needed based on the query and route accordingly.

    Args:
        state (dict): The current graph state containing the query.

    Returns:
        str: Next node to call ("web_search" or "generate").
    """

    print("---SEARCH NEED CHECK---")
    query = state["query"]

    # Use the need_of_search function to determine if a web search is necessary
    search_decision = need_of_search(query)

    # Extract the binary_score from the result
    binary_score = search_decision.binary_score

    # Route the question based on the search decision
    if binary_score == 'yes':
        print("---SEARCH IS NEEDDED, TO WEB SEARCH---")
        return "web_search"
    elif binary_score == 'no':
        print("---SEARCH IS NOT NEEDDED, TO GENERATE---")
        return "generate"


def its_the_first(state):
    """
    Check if this is the first interaction in the chat history.

    Args:
        state (dict): The current state (not used in this function but passed for compatibility).

    Returns:
        str: "first_prompt?" if no previous messages exist, otherwise "decider".
    """
    chat_history = memory.get_chat_history()
    if len(chat_history.messages) == 0:
        return "first_prompt?"
    else:
        return "decider"

def decide_to_generate(state):
  """
  Determines whether to generate an answer, or re-generate a question.

  Args:
      state (dict): The current graph state

  Returns:
      str: Binary decision for next node to call
  """

  print("---ASSESS TRESHOLD DOCUMENTS---")
  state["query"]
  filtered_documents = state["context"]
  cont = state.get("count", 0)
  if cont < 5: #to dont have an infinite loop
    if not filtered_documents:
      # All documents have been filtered check_relevance
      # We will re-generate a new query
      print(
          "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
      )
      cont = cont +1
      state['count'] = cont
      return "transform_query"
    else:
      # We have relevant documents, so generate answer
      print("---DECISION: GENERATE---")
      return "generate"
  else:
    print("---DECISION: GENERATE---")
    return "generate"
    
def City_router(state):
    """
    Route the question based on the presence of a city in the query.

    Args:
        state (dict): The current graph state containing the query.
    
    Returns:
        str: The path to follow, based on: "no_city" or "Has_city".
    """
    print("---CITY QUESTION---")
    query = state["query"]
    response = Hascity_func(query)
    if response.binary_score == "no":
        print("---No city, going to router---")
        return "no_city"
    elif response.binary_score == "yes":
        print("---City info---")
        return "Has_city"