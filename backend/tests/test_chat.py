from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chat_request_validation():
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
    assert "answer" in body
    assert "sources" in body


def test_chat_question_required():
    response = client.post(
        "/chat",
        json={"repository_id": "repo_123", "messages": []},
    )

    assert response.status_code == 422
