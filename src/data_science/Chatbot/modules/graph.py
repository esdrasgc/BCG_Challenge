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
        context: list of documents
        messages: list of preview messages
    """

    query: str
    generation: str
    choice: str
    context: List[str]
    messages: List[str]
    count: int

def graph_init():
    workflow = StateGraph(GraphState)
    workflow.add_node("first_prompt?", nodes.first_prompt)
    workflow.add_node("city_node", nodes.city_node)
    workflow.add_node('decider', nodes.decider)
    workflow.add_node("web_search", nodes.web_search)  # web search
    workflow.add_node("retrieve", nodes.retrieve)  # retrieve
    workflow.add_node("same", nodes.same)
    workflow.add_node("treshold_check", nodes.treshold_check)  # grade documents
    workflow.add_node("transform_query", nodes.transform_query)  # transform_query
    workflow.add_node("generate", nodes.generate)  # generate



    # Build graph with the edges
    workflow.add_conditional_edges(
        START,
        edges.its_the_first,
        {
            "first_prompt?": "first_prompt?",
            "decider": "decider",
        },
    )                      #If it is the first prompt goes to the city_node

    workflow.add_conditional_edges(
        "first_prompt?",
        edges.City_router,
        {
            "no_city": "decider",
            "Has_city": "city_node",
        },
    )

    workflow.add_edge("city_node", "decider")

    workflow.add_conditional_edges(
        "decider",
        edges.route_question,
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
        edges.DoSearch,
        {
            "web_search": "web_search",
            "generate": "generate",
        },
    )

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
    workflow.add_edge("generate", END)

    # Compile
    app = workflow.compile()
    return app

def chat(config, graph, query: str = None):
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
    config = memory.generate_session_id()  
    print("Bem-vindo ao chatbot! Digite 'sair' para encerrar a conversa.")
    
    while True:
        query = str(input("Você: "))
        if query.lower() == "sair":
            print("Conversa encerrada. Até mais!")
            break
        chat(config, graph, query)


