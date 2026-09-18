import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.models.schemas import RepositoryCreateRequest, RepositoryResponse
from app.services.github import parse_github_url
from app.services.ingestion import ingest_repository
from app.services.vector_store import repository_is_indexed

router = APIRouter(prefix="/repositories", tags=["repositories"])
REPOSITORY_STORE = {}


def _repository_id_for_url(github_url: str) -> str:
    owner, repo_name = parse_github_url(github_url)
    return f"repo_{owner}_{repo_name}"


def _repository_path(storage_root: Path, github_url: str) -> Path:
    owner, repo_name = parse_github_url(github_url)
    return storage_root / f"{owner}__{repo_name}"


@router.post("", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
def create_repository(payload: RepositoryCreateRequest):
    github_url = str(payload.github_url)

    try:
        repo_id = _repository_id_for_url(github_url)
        storage_root = Path(get_settings()["repo_storage_path"])
        storage_root.mkdir(parents=True, exist_ok=True)
        existing_path = _repository_path(storage_root, github_url)
        if existing_path.exists() and repository_is_indexed(repo_id):
            repository = RepositoryResponse(
                repository_id=repo_id,
                status="ready",
                message="Repository was already indexed and is ready to use.",
                github_url=github_url,
                local_path=str(existing_path.resolve()),
            )
            REPOSITORY_STORE[repo_id] = repository.model_dump(mode="python")
            return repository
        result = ingest_repository(github_url, storage_root=storage_root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    repository = RepositoryResponse(
        repository_id=repo_id,
        status="ready",
        message=(
            f"Repository indexed and ready. "
            f"Loaded {result['file_count']} files into {result['chunk_count']} chunks."
        ),
        github_url=github_url,
        local_path=result["local_path"],
    )
    REPOSITORY_STORE[repo_id] = repository.model_dump(mode="python")
    return repository


@router.get("/{repository_id}", response_model=RepositoryResponse)
def get_repository(repository_id: str):
    repository = REPOSITORY_STORE.get(repository_id)
    if repository is None:
        raise HTTPException(status_code=404, detail="Repository not found.")

    return RepositoryResponse(**repository)


@router.delete("/{repository_id}", response_model=dict)
def delete_repository(repository_id: str):
    repository = REPOSITORY_STORE.get(repository_id)
    if repository is None:
        raise HTTPException(status_code=404, detail="Repository not found.")

    local_path = repository.get("local_path")
    if local_path and Path(local_path).exists():
        shutil.rmtree(local_path, ignore_errors=True)

    del REPOSITORY_STORE[repository_id]
    return {"repository_id": repository_id, "deleted": True}
