from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_hello():
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json()["project"] == "LexiPy"

def test_analysis_returns_tokens():
    response = client.post("/api/analisar", json={"codigo": 'x = 10\nprint("oi")'})
    assert response.status_code == 200
    data = response.json()
    assert data["sucesso"] is True
    assert data["recebido"] is True
    assert data["tokens"]
    assert data["erros"] == []
    assert data["status"] == "success"

def test_lexical_error_is_returned_as_analysis_result():
    response = client.post("/api/analisar", json={"codigo": "x = @"})
    assert response.status_code == 200
    data = response.json()
    assert data["sucesso"] is False
    assert data["erros"][0]["lexema"] == "@"
    assert data["status"] == "lexical_errors"

def test_empty_code_is_rejected():
    response = client.post("/api/analisar", json={"codigo": "   \n "})
    assert response.status_code == 422

def test_missing_field_is_rejected():
    response = client.post("/api/analisar", json={})
    assert response.status_code == 422

def test_token_positions_are_present():
    response = client.post("/api/analisar", json={"codigo": "\n  valor = 3"})
    token = next(t for t in response.json()["tokens"] if t["lexema"] == "valor")
    assert token["linha"] == 2
    assert token["coluna"] == 3
