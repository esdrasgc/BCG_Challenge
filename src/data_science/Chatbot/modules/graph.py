from typing import List
import langchain
from langgraph.graph import END, StateGraph, START
from typing_extensions import TypedDict
import pprint
import langgraph

import memory
import nodes
import edges
from IPython.display import Image, display


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        query: query
        generation: LLM generation
        choice: choice of the path to follow
        context: list of documents
        messages: list of preview messages
        count: count of the number of times the same query was re-generated, to avoid infinite loops
    """

    query: str
    generation: str
    choice: str
    context: List[str]
    messages: List[str]
    count: int
    infos: str

def graph_init():
    """
    Initialize and configure the state graph workflow for routing queries and generate the output.

    Returns:
        app: The compiled workflow application.
    """
    
    # Initialize the graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("first_prompt?", nodes.first_prompt) # check if it is the first prompt
    workflow.add_node("city_node", nodes.city_node) # the city_node gets info about the city
    workflow.add_node('decider', nodes.decider) # decides the path to follow
    workflow.add_node("web_search", nodes.web_search)  # Do a web search to pass as context
    workflow.add_node("retrieve", nodes.retrieve)  # retrieve documents to pass as context
    workflow.add_node("same", nodes.same) # A suport node to keep the graph flow after a edge decision
    workflow.add_node("treshold_check", nodes.treshold_check)  # grade documents
    workflow.add_node("transform_query", nodes.transform_query)  # transform_query if all documents are not relevant
    workflow.add_node("generate", nodes.generate)  # generate the final output



    # Building the graph with the edges:


    workflow.add_conditional_edges(
        START,
        edges.its_the_first, # Checks if this is the first interaction
        {
            "first_prompt?": "first_prompt?",
            "decider": "decider",
        },
    )                     

    workflow.add_conditional_edges(
        "first_prompt?",
        edges.City_router, # Routes based on whether a city is mentioned
        {
            "no_city": "decider",
            "Has_city": "city_node",
        },
    )

    # Directs the flow from city_node to decider
    workflow.add_edge("city_node", "decider")

    workflow.add_conditional_edges(
        "decider",
        edges.route_question, # Routes based on query classification
        {
            "Need": "same",
            "general": "retrieve",
            "small_city": "retrieve",
            "medium_city":"retrieve",
            "big_city" : "retrieve",

        },
    )
    workflow.add_conditional_edges(
        "same",
        edges.DoSearch, # Determines if a web search is needed
        {
            "web_search": "web_search",
            "generate": "generate",
        },
    )

    #Simple and mandatory edges
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("retrieve", "treshold_check")
    workflow.add_conditional_edges(
        "treshold_check",
        edges.decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate",
        },
    )

    workflow.add_edge("transform_query", "retrieve")
    
    # End of the graph
    workflow.add_edge("generate", END)

    # Compile
    app = workflow.compile()
    return app

def chat(config, graph, query: str = None):
  """
    Manage user interaction with the chat system and process the query through the state graph.

    Args:
        config (dict): Configuration parameters for the chat system.
        graph (StateGraph): The state graph used for processing the query.
        query (str, optional): the user prompt.

    prints the output of the graph
"""
  if query == None:
    query = str(input("Você: "))
  inputs = {
    "query":  query
  }

  for output in graph.stream(inputs, config):
      for key, value in output.items():
          # Node
          print(f"Node '{key}':")
          # Optional: print full state at each node
          # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
      print("\n---\n")    
  print(value["generation"])

def chatbot(graph):
    """
    Main function to run the chatbot, this loops over the chat function to generate a chat with an unique id.

    Args:
        graph (StateGraph): The state graph used for processing the query.
    """

    config = memory.generate_session_id()  
    print("Bem-vindo ao chatbot! Digite 'sair' para encerrar a conversa.")
    
    while True:
        query = str(input("Você: "))
        if query.lower() == "sair":
            print("Conversa encerrada. Até mais!")
            break
        chat(config, graph, query)


