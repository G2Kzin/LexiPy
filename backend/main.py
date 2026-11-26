import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from scanner import scan
from parser import parse, ErroSintatico
from intermediate import gerar_codigo_intermediario

app = FastAPI(title="LexiPy API", version="0.5.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class CodeRequest(BaseModel):
    codigo: str


class ExplainLineRequest(BaseModel):
    codigo: str = Field(min_length=1, max_length=20000)
    linha: int = Field(ge=1)


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
        "sintaxe_sucesso": None, "ast": None, "erros_sintaticos": [],
        "codigo_intermediario": None
    }
    if resultado["sucesso"]:
        try:
            ast = parse(payload.codigo)["ast"]
            resposta["ast"] = ast
            resposta["codigo_intermediario"] = gerar_codigo_intermediario(ast)
            resposta["sintaxe_sucesso"] = True
            resposta["mensagem"] = "Análise léxica e sintática concluídas."
            resposta["status"] = "success"
        except ErroSintatico as exc:
            resposta["sintaxe_sucesso"] = False
            resposta["erros_sintaticos"] = [{
                "tipo": "ERRO_SINTATICO", "mensagem": exc.mensagem,
                "linha": exc.linha, "coluna": exc.coluna
            }]
            resposta["mensagem"] = "Análise léxica concluída; foram encontrados erros sintáticos."
            resposta["status"] = "syntax_errors"
    return resposta


@app.post("/api/explicar-linha")
async def explicar_linha(payload: ExplainLineRequest):
    linhas = payload.codigo.splitlines()
    if payload.linha > len(linhas):
        raise HTTPException(status_code=422, detail="A linha informada não existe no código.")
    trecho = linhas[payload.linha - 1]
    if not trecho.strip():
        raise HTTPException(status_code=422, detail="A linha selecionada está vazia.")

    base_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")
    modelo = os.getenv("OLLAMA_MODEL", "llama3.2")
    prompt = (
        "Você é um tutor de programação e de compiladores. Explique em português brasileiro, "
        "com linguagem simples e didática, o que a linha selecionada faz. Considere o contexto "
        "do código, explique os símbolos e conceitos relevantes sem inventar comportamento. "
        "Não execute o código. Se houver dependência de outra linha, mencione-a brevemente. "
        "Responda em até 120 palavras.\n\n"
        f"Código completo:\n{payload.codigo}\n\n"
        f"Linha selecionada ({payload.linha}): {trecho}"
    )
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{base_url}/api/chat",
                json={
                    "model": modelo,
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": "Você é o assistente educacional do LexiPy."},
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            response.raise_for_status()
            data = response.json()
            explicacao = data.get("message", {}).get("content", "").strip()
            if not explicacao:
                raise ValueError("O modelo não retornou uma explicação.")
            return {"linha": payload.linha, "codigo": trecho, "explicacao": explicacao, "modelo": modelo}
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Não foi possível consultar o Llama. Verifique se o Ollama está iniciado "
                f"e se o modelo '{modelo}' está instalado. Detalhe: {str(exc)[:180]}"
            )
        ) from exc
