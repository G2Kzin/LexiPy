from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scanner import scan

app = FastAPI(title="LexiPy API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        raise HTTPException(
            status_code=422,
            detail="Informe um código-fonte antes de solicitar a análise."
        )

    resultado = scan(payload.codigo)
    return {
        # Campos novos da Etapa 3
        "sucesso": resultado["sucesso"],
        "tokens": resultado["tokens"],
        "erros": resultado["erros"],
        # Campos mantidos para compatibilidade com a Etapa 2
        "mensagem": (
            "Análise léxica concluída."
            if resultado["sucesso"]
            else "Análise concluída com erro(s) léxico(s)."
        ),
        "recebido": True,
        "caracteres": len(payload.codigo),
        "linhas": len(payload.codigo.splitlines()) or 1,
        "status": "success" if resultado["sucesso"] else "lexical_errors",
    }
