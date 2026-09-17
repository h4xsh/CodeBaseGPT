from pathlib import Path

from app.services.github import clone_repository, get_repository_name, parse_github_url


def ingest_repository(github_url: str, storage_root: str | Path | None = None):
    owner, repo_name = parse_github_url(github_url)
    local_path = clone_repository(github_url, storage_root=storage_root)

    return {
        "repository_id": f"repo_{owner}_{repo_name}",
        "github_url": github_url,
        "owner": owner,
        "name": repo_name,
        "local_path": local_path,
        "status": "ready",
    }
