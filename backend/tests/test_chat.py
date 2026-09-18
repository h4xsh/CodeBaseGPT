from fastapi.testclient import TestClient

from app.main import app
from app.api import chat as chat_api

client = TestClient(app)


def test_chat_request_validation(monkeypatch):
    monkeypatch.setattr(
        chat_api,
        "answer_question",
        lambda **kwargs: {"answer": "Answer", "sources": []},
    )
    response = client.post(
        "/chat",
        json={
            "repository_id": "repo_123",
            "question": "How does authentication work?",
            "messages": [{"role": "user", "content": "Hello"}],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {"answer": "Answer", "sources": []}


def test_chat_question_required():
    response = client.post(
        "/chat",
        json={"repository_id": "repo_123", "messages": []},
    )

    assert response.status_code == 422
