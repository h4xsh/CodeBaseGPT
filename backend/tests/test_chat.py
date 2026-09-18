from fastapi.testclient import TestClient

from app.main import app
from app.api import chat as chat_api

client = TestClient(app)


def test_chat_request_validation(monkeypatch):
    monkeypatch.setattr(
        chat_api,
        "answer_question",
        lambda **kwargs: {"answer": "Answer", "sources": [], "model": "qwen3:8b"},
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
    assert body == {"answer": "Answer", "sources": [], "model": "qwen3:8b"}


def test_chat_question_required():
    response = client.post(
        "/chat",
        json={"repository_id": "repo_123", "messages": []},
    )

    assert response.status_code == 422


def test_stream_chat_returns_server_sent_events(monkeypatch):
    monkeypatch.setattr(
        chat_api,
        "stream_question",
        lambda **kwargs: (
            iter(["** streamed", " answer **"]),
            [{"file_path": "main.py", "snippet": "print(1)", "chunk_index": 0, "score": 0.1}],
        ),
    )

    response = client.post(
        "/chat/stream",
        json={"repository_id": "repo_123", "question": "What does it do?"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert '"type": "token"' in response.text
    assert '"type": "done"' in response.text
    assert "main.py" in response.text
