import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.models.schemas import RepositoryCreateRequest, RepositoryResponse
from app.services.github import clone_repository, parse_github_url

router = APIRouter(prefix="/repositories", tags=["repositories"])
REPOSITORY_STORE = {}


def _repository_id_for_url(github_url: str) -> str:
    owner, repo_name = parse_github_url(github_url)
    return f"repo_{owner}_{repo_name}"


@router.post("", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
def create_repository(payload: RepositoryCreateRequest):
    github_url = str(payload.github_url)

    try:
        repo_id = _repository_id_for_url(github_url)
        storage_root = Path(get_settings()["repo_storage_path"])
        storage_root.mkdir(parents=True, exist_ok=True)
        local_path = clone_repository(github_url, storage_root=storage_root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    repository = RepositoryResponse(
        repository_id=repo_id,
        status="ready",
        message="Repository cloned and ready for processing.",
        github_url=github_url,
        local_path=local_path,
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
