from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="LexiPy API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class CodeRequest(BaseModel):
    codigo: str

@app.get("/api/health")
def health():
    return {"status": "healthy"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello, World!", "project": "LexiPy", "status": "success"}

@app.post("/api/analisar")
def analisar(payload: CodeRequest):
    if not payload.codigo.strip():
        raise HTTPException(status_code=422, detail="Informe um código-fonte antes de solicitar a análise.")
    # Nesta etapa, apenas recebemos e validamos a entrada; o lexer será implementado depois.
    return {
        "mensagem": "Código recebido com sucesso. A análise léxica será implementada em uma próxima etapa.",
        "recebido": True,
        "caracteres": len(payload.codigo),
        "linhas": len(payload.codigo.splitlines()) or 1,
        "status": "received"
    }
