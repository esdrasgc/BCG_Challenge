# Project Setup Instructions

### Prerequisites

Ensure you have the following programs installed:
- Docker
- Python 3.12
- Pip
- Bash

### Setup for chatbot utilization:

For the setup of the enviroment, you can run the command:
```bash
./setup.sh
```
It will guide you to creating the .env file (if there is none), installing python (if it's not present), and then creating an enviroment to install all the libs.  
Then it creates an docker netowrk named "chat_network", initiates the postgresql container and ingest the data from the documents, saved in the "data_science\RAG_Engineering\embedded_files" folder. 

### Running the chatbot:

To run the chatbot, you can use the command:
```bash
./run.sh
```
In the fisrt time, it will build the backend and frontend aplications to a docker image. When the script is completed, the [localhost](http://localhost) should display the frontend of the chatbot implementation. 

### Setup and run:

If you want to run a command and come back only when it's ready, you can run the command:
```bash
./setup_and_run.sh
```
It calls both of the scripts described before. 

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
