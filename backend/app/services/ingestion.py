from pathlib import Path

from app.services.chunker import chunk_files
from app.services.file_loader import load_repository_files
from app.services.github import clone_repository, parse_github_url
from app.services.vector_store import add_chunks, delete_repository


def ingest_repository(github_url: str, storage_root: str | Path | None = None):
    owner, repo_name = parse_github_url(github_url)
    local_path = clone_repository(github_url, storage_root=storage_root)
    files = load_repository_files(local_path)
    if not files:
        raise RuntimeError("Repository has no supported readable source files.")

    chunks = chunk_files(files)
    if not chunks:
        raise RuntimeError("Repository produced no searchable chunks.")

    repository_id = f"repo_{owner}_{repo_name}"
    delete_repository(repository_id)
    add_chunks(repository_id, chunks)

    return {
        "repository_id": repository_id,
        "github_url": github_url,
        "owner": owner,
        "name": repo_name,
        "local_path": local_path,
        "file_count": len(files),
        "chunk_count": len(chunks),
        "status": "ready",
    }
