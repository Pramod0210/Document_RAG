# tests/test_unit_cases.py

import pytest
from fastapi.testclient import TestClient
from api.main import app   # or your FastAPI entrypoint

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "Document RAG" in response.text

def test_upload_pdf():
    with open("tests/sample.pdf", "rb") as f:
        response = client.post("/chat/index", files={"file": ("sample.pdf", f, "application/pdf")})
    assert response.status_code == 200


def test_chat_query():
    response = client.post("/chat/query", data={"question": "What is AI?", "k": 3})
    assert response.status_code == 200
    assert "answer" in response.json()

def test_invalid_session_id():
    response = client.post("/chat/query", data={"question": "Test", "use_session_dirs": True, "session_id": "invalid"})
    assert response.status_code == 404

def test_upload_unsupported_file():
    with open("tests/sample.exe", "rb") as f:
        response = client.post("/chat/index", files={"file": ("sample.exe", f, "application/octet-stream")})
    assert response.status_code == 400

def test_upload_csv():
    with open("tests/sample.csv", "rb") as f:
        response = client.post("/chat/index", files={"file": ("sample.csv", f, "text/csv")})
    assert response.status_code == 200

def test_empty_question():
    response = client.post("/chat/query", data={"question": ""})
    assert response.status_code == 400 or response.status_code == 422

def test_evaluation_matrix():
    response = client.post("/eval", data={"question": "Test", "answer": "Test answer"})
    assert response.status_code == 200
    assert "score" in response.json()