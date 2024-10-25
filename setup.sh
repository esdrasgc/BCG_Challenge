./setup_env.sh

cp .env ./vector_db/
cp .env ./backend/

./setup_python.sh

./unset_env_vars.sh

docker network create chat-network

cd vector_db/

docker-compose down

docker-compose up -d 

cd ..

source ./venv/bin/activate

python ./check_db_and_create.py

python ./data_science/RAG_Engineering/main_faster.py

cd vector_db/

docker-compose down

