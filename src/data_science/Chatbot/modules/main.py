import os
from dotenv import load_dotenv
import openai
import graph 
import memory
import utils
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import db
import pandas as pd

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")


openai.api_key = openai_api_key


os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

client = openai.OpenAI(api_key=openai_api_key)

# Load the file
embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')
db_total = db.fetch_all_data()
db_total = pd.DataFrame(db_total)
db_small = db_total[db_total[1] == 'itabirito_embedding']
db_medium = db_total[(db_total[1] == 'curitiba_embedding') | (db_total[1] == 'joao_pessoa_embedding')]
db_big = db_total[db_total[1] == 'sao_paulo_embedding']
db_total = db_total[(db_total[1] == 'enfrentamento_embedding') | 
                    (db_total[1] == 'agro_embedding') | 
                    (db_total[1] == 'federal_embedding') | 
                    (db_total[1] == 'nacional_embedding')]
app = graph.graph_init()
config = memory.generate_session_id()
graph.chatbot(graph=app)

