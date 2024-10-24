./setup_env.sh

cp .env ./vector_db/

./setup_python.sh

docker network create chat-network

cd vector_db/

docker-compose down

docker-compose up -d 

cd ..

source /venv/bin/activate

python ./data_science/RAG_Engineering/main_faster.py

cd vector_db/

docker-compose down

