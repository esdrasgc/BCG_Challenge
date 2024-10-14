from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Permitir todas as origens (CORS para desenvolvimento)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Classe Pydantic para validar a requisição
class IncrementRequest(BaseModel):
    text: str
    value: int

# Função de incremento simples
def increment(value: int) -> int:
    return value + 1

# Rota que recebe um texto, incrementa o valor e devolve o texto concatenado com o valor incrementado
@app.post("/increment/")
async def increment_text(request: IncrementRequest):
    incremented_value = increment(request.value)
    return {"result": f"{request.text} {incremented_value}"}

# Executando o servidor
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
