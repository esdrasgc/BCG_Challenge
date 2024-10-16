
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def connect_db():
    """
    Establish a connection to the database and return both the connection and cursor objects.

    Returns:
        conn (psycopg2.extensions.connection): Database connection object.
        cursor (psycopg2.extensions.cursor): Cursor object to interact with the database.
    """

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
    """
    Execute a search query on the database and return the result set.

    Args:
        query_sql (str): SQL query string to be executed.
        params (tuple, optional): Parameters to safely inject into the SQL query (default is None).

    Returns:
        result (list of tuples): Result set returned from the database query, where each tuple represents a row.
    """
    conn, cursor = connect_db()
    cursor.execute(query_sql, params)
    result = cursor.fetchall()
    close_connection(conn, cursor)
    return result

def fetch_all_data():
    """    
    Executes a query to retrieve all data from the 'semanticembeddingfast' table.

    Returns:
        result (list of tuples): All rows from the embeddings table.
    """
    
    query_sql = "SELECT * FROM semanticembeddingfast"
    return fetch_data(query_sql)