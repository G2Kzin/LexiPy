import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_hello_regression():
    response = client.get('/api/hello')
    assert response.status_code == 200
    assert response.json()["project"] == "LexiPy"

def test_receives_python_code():
    response = client.post('/api/analisar', json={"codigo": "print('Olá')"})
    assert response.status_code == 200
    assert response.json()["recebido"] is True
    assert response.json()["caracteres"] == len("print('Olá')")

def test_rejects_empty_code():
    response = client.post('/api/analisar', json={"codigo": ""})
    assert response.status_code == 422

def test_rejects_whitespace_code():
    response = client.post('/api/analisar', json={"codigo": "  \n\t "})
    assert response.status_code == 422

def test_rejects_missing_field():
    response = client.post('/api/analisar', json={})
    assert response.status_code == 422

def test_accepts_special_characters_as_text():
    code = "# teste\ntexto = '<>&\\\"'"
    response = client.post('/api/analisar', json={"codigo": code})
    assert response.status_code == 200
    assert response.json()["recebido"] is True
