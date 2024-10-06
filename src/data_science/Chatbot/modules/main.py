import os
from dotenv import load_dotenv
import openai
import graph 
import memory
import utils
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

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
db = FAISS.load_local(r"C:\Users\felip\Desktop\dab", embeddings, allow_dangerous_deserialization=True)
app = graph.graph_init()
config = memory.generate_session_id()
graph.chatbot(graph=app)

