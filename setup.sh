./setup_env.sh

./setup_python.sh

cd vector_db

docker compose down

docker compose up -d

cd ..

python ./data_science/RAG_Engineering/main_faster.py

