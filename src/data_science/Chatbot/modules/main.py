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

# Load environment variables from .env
load_dotenv()

#Load the API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")

openai.api_key = openai_api_key

os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

#Initialize the OpenAI client
client = openai.OpenAI(api_key=openai_api_key)

# Load the embeddings model
embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')

# Load the vectorstore and create the specific vectorstores
db_total = db.fetch_all_data()
db_total = pd.DataFrame(db_total)
db_small = db_total[db_total[1] == 'itabirito_embedding']
db_medium = db_total[(db_total[1] == 'curitiba_embedding') | (db_total[1] == 'joao_pessoa_embedding')]
db_big = db_total[db_total[1] == 'sao_paulo_embedding']
db_total = db_total[(db_total[1] == 'enfrentamento_embedding') | 
                    (db_total[1] == 'agro_embedding') | 
                    (db_total[1] == 'federal_embedding') | 
                    (db_total[1] == 'nacional_embedding')]

# Initialize the graph
app = graph.graph_init()
#Generate a session id for memory management
config = memory.generate_session_id()
#Star the chatbot
graph.chatbot(graph=app)

