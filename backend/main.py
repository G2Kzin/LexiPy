from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scanner import scan
from parser import parse, ErroSintatico

app = FastAPI(title="LexiPy API", version="0.4.0")
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
    resultado = scan(payload.codigo)
    resposta = {
        "sucesso": resultado["sucesso"], "tokens": resultado["tokens"], "erros": resultado["erros"],
        "mensagem": "Análise léxica concluída." if resultado["sucesso"] else "Análise concluída com erro(s) léxico(s).",
        "recebido": True, "caracteres": len(payload.codigo),
        "linhas": len(payload.codigo.splitlines()) or 1,
        "status": "success" if resultado["sucesso"] else "lexical_errors",
        "sintaxe_sucesso": None, "ast": None, "erros_sintaticos": []
    }
    if resultado["sucesso"]:
        try:
            resposta["ast"] = parse(payload.codigo)["ast"]
            resposta["sintaxe_sucesso"] = True
            resposta["mensagem"] = "Análise léxica e sintática concluídas."
            resposta["status"] = "success"
        except ErroSintatico as exc:
            resposta["sintaxe_sucesso"] = False
            resposta["erros_sintaticos"] = [{"tipo": "ERRO_SINTATICO", "mensagem": exc.mensagem,
                                               "linha": exc.linha, "coluna": exc.coluna}]
            resposta["mensagem"] = "Análise léxica concluída; foram encontrados erros sintáticos."
            resposta["status"] = "syntax_errors"
    return resposta
