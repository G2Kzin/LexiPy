from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_valid_code_returns_tokens_and_ast():
    response = client.post("/api/analisar", json={"codigo": "x = 10\nprint(x)"})
    assert response.status_code == 200
    data = response.json()
    assert data["sucesso"] is True
    assert data["sintaxe_sucesso"] is True
    assert data["ast"]["tipo"] == "Programa"
    assert data["status"] == "success"


def test_syntax_error_is_distinguished_from_lexical_error():
    response = client.post("/api/analisar", json={"codigo": "x = 1 +"})
    assert response.status_code == 200
    data = response.json()
    assert data["sucesso"] is True
    assert data["sintaxe_sucesso"] is False
    assert data["erros_sintaticos"][0]["tipo"] == "ERRO_SINTATICO"
    assert data["status"] == "syntax_errors"


def test_lexical_error_prevents_syntax_analysis():
    response = client.post("/api/analisar", json={"codigo": "x = @"})
    data = response.json()
    assert data["sucesso"] is False
    assert data["sintaxe_sucesso"] is None
    assert data["status"] == "lexical_errors"
