# Climate advisor assistant

The climate advisor project is a chatbot using Retrieval-Augmented Generation (RAG) techniques to assist municipal managers in creating climate adaptation plans.

## Setup and run the Chatbot

### Prerequisites

Ensure you have the following programs installed:
- Docker
- Python 3.12
- Pip
- Bash

Obs.: make sure that all the scripts in the root dir are enabled to execution

### Setup for chatbot utilization:

For the setup of the enviroment, you can run the command:
```bash
./setup.sh
```
It will guide you to creating the .env file (if there is none), installing python (if it's not present), and then creating an enviroment to install all the libs.  
Then it creates an docker network named "chat-network", initiates the postgresql container and ingest the data from the documents, saved in the "data_science\RAG_Engineering\embedded_files" folder. 

### Running the chatbot:

To run the chatbot, you can use the command:
```bash
./run.sh
```
In the fisrt time, it will build the backend and frontend aplications to a docker image. When the script is completed, the [localhost](http://localhost) should display the frontend of the chatbot implementation. Please wait like for a minute before click the button "start chat", after this little time the bot will be ready to use. 

### Setup and run:

If you want to run a command and come back only when it's ready, you can run the command:
```bash
./setup_and_run.sh
```
It calls both of the scripts described before. 



## Project breakdown

### Vector_db

In the vector-db dir is a simple postgresql database with the vector extension added to it. To run it, you should create a docker network named "chat-network" and then run the docker container. Use the commands:

```bash
docker network create chat-network
cd vector_db/
docker-compose up -d 
```

### Preprocessing data

In this dir there is two scripts to get the raw data from the pdfs from the "data/raw" and make some simple text extractation and cleaning, and saves them to the "data/bronze" dir. To use them you can run the scripts:

```bash
python preprocessing_data/raw_to_pre_processed.py
python preprocessing_data/pre_processed_to_bronze.py
```


### Data science

This dir contains the logic to tokenize the text, separate it in chunks and save it on DB (RAG_Engineering) and a CLI implementation on the RAG assistant (Chatbot), using graph for decisions and openai for generating the response.

#### Rag Engineering

Here the txt files are transformed in embbedings, using a Semantic chunker to make sure the context is maintained, and saved into the embedded_files dir, then ingest to the database. To use this you can run the command:
```bash
python data_science/RAG_Engineering/main.py
```

Since the data is already in the embedded_files dir, you can use the command below to ingest the data into the database.
```bash
python data_science/RAG_Engineering/main_faster.py
```

#### Chatbot

It's the CLI implementation of the assistant, mainly used for developing and testing. To use the CLI chat you may run the commands:
```bash
cd data_science/Chatbot/modules
python main.py
```


### Backend

The backend is a fastapi app, using SQLmodel to save the messages and interactions with the chat. The dir contains the main.py and api_models.py files, to implement the API, and a copy from the files of chatbot cli implementation, with some adaptations to make it work as an API.  
To run it, you can use: 

docker:
```bash
docker compose up -d
```

or running the app directly (ensure the database is available):
```bash
cd backend/
python main.py
```

### Frontend

The frontend is a next application with a simple UI. It has two pages:
1. Location Selection: It displays a select box to all the states and cities from Brazil
2. Chatbot: The chatbot page with some Key Challenges of the city  

You can run it using:  

docker:
```bash
docker compose up -d
```

or npm:

To run it in the development mode:
```bash
npm run dev
```

To run it in production mode:
```bash
npm run build
npm run start
```
Obs.: you will need to have node and npm installed to run these commands. It's not a prerequisite of the project because you can run it using docker.



