from pathlib import Path

from app.services import ingestion


def test_ingest_repository_indexes_loaded_chunks(monkeypatch, tmp_path: Path):
    repository_path = tmp_path / "repo"
    repository_path.mkdir()
    files = [{"path": "main.py", "content": "print('hello')"}]
    chunks = [{"content": "print('hello')", "file_path": "main.py", "chunk_index": 0}]
    captured = {}

    monkeypatch.setattr(ingestion, "clone_repository", lambda *args, **kwargs: str(repository_path))
    monkeypatch.setattr(ingestion, "load_repository_files", lambda path: files)
    monkeypatch.setattr(ingestion, "chunk_files", lambda loaded: chunks)
    monkeypatch.setattr(ingestion, "delete_repository", lambda repository_id: captured.setdefault("deleted", repository_id))
    monkeypatch.setattr(
        ingestion,
        "add_chunks",
        lambda repository_id, indexed_chunks: captured.update(
            added=(repository_id, indexed_chunks)
        ) or len(indexed_chunks),
    )

    result = ingestion.ingest_repository(
        "https://github.com/example/repository",
        storage_root=tmp_path,
    )

    assert result["status"] == "ready"
    assert result["file_count"] == 1
    assert result["chunk_count"] == 1
    assert captured["deleted"] == "repo_example_repository"
    assert captured["added"] == ("repo_example_repository", chunks)


def test_ingest_repository_rejects_empty_repository(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(ingestion, "clone_repository", lambda *args, **kwargs: str(tmp_path))
    monkeypatch.setattr(ingestion, "load_repository_files", lambda path: [])

    try:
        ingestion.ingest_repository("https://github.com/example/repository", tmp_path)
        assert False, "Expected empty repositories to be rejected"
    except RuntimeError as exc:
        assert "no supported" in str(exc)
