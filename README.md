# Project Setup Instructions

### Prerequisites
- Ensure you have Docker installed on your machine.

### Setting Up the Vector Database
1. Navigate to the `vector_db` folder:
   ```bash
   cd vector_db
    ```
2.Run the following command to start the vector database in detached mode:
```bash
docker compose up -d
```
This will initialize the Vector DB using Docker.

### Creating the Tables
To create the required tables in the database, run the Python script located at data_science/src/RAG_engeneering/main.py:
```bash
python data_science/src/RAG_engeneering/main.py
```
