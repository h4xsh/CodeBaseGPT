from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_repository_valid_request():
    response = client.post(
        "/repositories",
        json={"github_url": "https://github.com/microsoft/vscode"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["repository_id"] == "repo_microsoft_vscode"
    assert body["status"] == "ready"


def test_create_repository_invalid_url():
    response = client.post(
        "/repositories",
        json={"github_url": "https://example.com/repo"},
    )

    assert response.status_code == 422


def test_get_repository_not_found():
    response = client.get("/repositories/missing")

    assert response.status_code == 404
