from typing import Literal
from pydantic import BaseModel, Field
from langchain.prompts import (
    ChatPromptTemplate
)
import llm
import utils

model = llm.model_init()

### Edges functions:

    ###Router
class Initial_choice(BaseModel):
    """Route a user query to the most relevant datasource, the vectorstore or a web search."""

    datasource: Literal["vectorstore", "web_search"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )


def router_func(query:str, model = model):
  system = """You are an expert at routing a user question to a vectorstore or web search.
  The vectorstore contains documents in portuguese related to climate plans for cities in Brazil.
  Use the vectorstore for questions on these topics. Otherwise, use web-search."""
  route_prompt = ChatPromptTemplate.from_messages(
      [
          ("system", system),
          ("human", "{query}"),
      ]
  )
  structured_model_router = model.with_structured_output(Initial_choice) #Will return or "vectorstore" or "web_search"
  question_router = route_prompt | structured_model_router
  return question_router.invoke({'query': query})

    ###Tell if a search is needed
class Search_need(BaseModel):
    """Binary score for tell the necessity of web search."""

    binary_score: str = Field(
        description="Is necessary to do a web search on the query, 'yes' or 'no'"
    )
def need_of_search(query:str, model = model):
  structured_model_needs = model.with_structured_output(Search_need)

  # Prompt
  system = """You are an assistant responsible for determining whether a web search is necessary based on a user's query. 
  You will receive a query and must decide if a web search is required. Provide a binary answer: 'yes' if the query cannot be answered without external information, or 'no' if it can be answered with available knowledge. 
  Remember that is a continuos chat, so the user can use references that the final assistant will know
  Use your internal knowledge to answer straightforward questions and only suggest a search when it is absolutely necessary.
  Your response format should strictly follow this structure:
  - binary_score: 'yes' or 'no'

  Do not provide any other information or explanations."""
   
  need_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: {query}"),
    ]
  )
  needs_router = need_prompt | structured_model_needs
  return needs_router.invoke({"query": query})


### Edges:

def route_question(state):
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    query = state["query"]
    source = router_func(query)
    if source.datasource == "web_search":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "Need"
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"
    
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
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "web_search"
    elif binary_score == 'no':
        print("---ROUTE QUESTION TO GENERATE---")
        return "generate"
    
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

    if not filtered_documents:
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
        )
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"