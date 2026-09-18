from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_repository_valid_request(monkeypatch):
    from app.api import repositories as repositories_api

    monkeypatch.setattr(
        repositories_api,
        "ingest_repository",
        lambda github_url, storage_root: {
            "local_path": str(storage_root / "microsoft__vscode"),
            "file_count": 2,
            "chunk_count": 3,
        },
    )
    monkeypatch.setattr(repositories_api, "repository_is_indexed", lambda repository_id: False)
    response = client.post(
        "/repositories",
        json={"github_url": "https://github.com/microsoft/vscode"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["repository_id"] == "repo_microsoft_vscode"
    assert body["status"] == "ready"
    assert "2 files" in body["message"]


def test_create_repository_reuses_existing_index(monkeypatch, tmp_path):
    from app.api import repositories as repositories_api

    existing_path = tmp_path / "microsoft__vscode"
    existing_path.mkdir()
    monkeypatch.setattr(
        repositories_api,
        "get_settings",
        lambda: {"repo_storage_path": str(tmp_path)},
    )
    monkeypatch.setattr(repositories_api, "repository_is_indexed", lambda repository_id: True)
    monkeypatch.setattr(
        repositories_api,
        "ingest_repository",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("should not re-ingest")),
    )

    response = client.post(
        "/repositories",
        json={"github_url": "https://github.com/microsoft/vscode"},
    )

    assert response.status_code == 201
    assert "already indexed" in response.json()["message"]


def test_repository_path_preserves_underscores(monkeypatch, tmp_path):
    from app.api import repositories as repositories_api

    existing_path = tmp_path / "team_tools__code_base"
    existing_path.mkdir()
    monkeypatch.setattr(
        repositories_api,
        "get_settings",
        lambda: {"repo_storage_path": str(tmp_path)},
    )
    monkeypatch.setattr(repositories_api, "repository_is_indexed", lambda repository_id: True)
    monkeypatch.setattr(
        repositories_api,
        "ingest_repository",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("should not re-ingest")),
    )

    response = client.post(
        "/repositories",
        json={"github_url": "https://github.com/team_tools/code_base"},
    )

    assert response.status_code == 201
    assert response.json()["local_path"].endswith("team_tools__code_base")


def test_create_repository_invalid_url():
    response = client.post(
        "/repositories",
        json={"github_url": "https://example.com/repo"},
    )

    assert response.status_code == 422


def test_get_repository_not_found():
    response = client.get("/repositories/missing")

    assert response.status_code == 404
