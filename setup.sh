./setup_env.sh

./setup_python.sh

docker network create chat-network

cd vector_db

docker compose down

docker compose up -d

cd ..

python ./data_science/RAG_Engineering/main_faster.py

