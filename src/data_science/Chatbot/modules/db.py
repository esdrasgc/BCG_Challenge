
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def connect_db():
    """Connects to the database and returns the connection and cursor."""

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),       # Ex: 'localhost' or Docker IP
        database=os.getenv("DB_NAME"),   # Name of the database
        user=os.getenv("DB_USER"),       # Database user
        password=os.getenv("DB_PASSWORD")  # Database password
    )
    cursor = conn.cursor()
    return conn, cursor

def close_connection(conn, cursor):
    """Closes the connection to the database."""
    cursor.close()
    conn.close()

def fetch_data(query_sql, params=None):
    """Executes a search query on the database and returns the result."""
    conn, cursor = connect_db()
    cursor.execute(query_sql, params)
    result = cursor.fetchall()
    close_connection(conn, cursor)
    return result

def fetch_all_data():
    """Fetches all data from the embeddings table."""
    query_sql = "SELECT * FROM semanticembeddingfast"
    return fetch_data(query_sql)