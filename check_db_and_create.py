import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

# Define connection parameters from .env
conn_params = {
    'dbname': 'postgres',  # Use 'postgres' to connect to the server initially
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# Get the target database name from .env
database_name = os.getenv('DB_NAME')

# Number of retries and delay
max_retries = 10
retry_delay = 2  # seconds

# Function to attempt a connection with retries
def connect_with_retries(params, max_retries, retry_delay):
    retries = 0
    while retries < max_retries:
        try:
            # Attempt to establish the connection
            conn = psycopg2.connect(**params)
            print("Connected to the PostgreSQL server successfully.")
            return conn
        except psycopg2.OperationalError as e:
            # Print error and retry after delay
            print(f"Connection failed: {e}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {retry_delay} seconds... ({retries}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Could not connect to the PostgreSQL server.")
                raise

# Attempt to connect to PostgreSQL with retries
conn = connect_with_retries(conn_params, max_retries, retry_delay)

# Enable autocommit for the connection
conn.autocommit = True

# Create a cursor object
cur = conn.cursor()

# Check if the database already exists
cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
exists = cur.fetchone()

if exists:
    print(f"Database '{database_name}' already exists.")
else:
    # Execute the CREATE DATABASE command if it doesn't exist
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
    print(f"Database '{database_name}' created successfully!")

# Close the cursor and connection for the 'postgres' database
cur.close()
conn.close()

# Reconnect to the newly created database (or existing one)
new_conn_params = conn_params.copy()
new_conn_params['dbname'] = database_name
conn = connect_with_retries(new_conn_params, max_retries, retry_delay)
conn.autocommit = True
cur = conn.cursor()

# Execute the CREATE EXTENSION command
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
print("Extension 'vector' created or already exists.")

# Close the cursor and connection
cur.close()
conn.close()
