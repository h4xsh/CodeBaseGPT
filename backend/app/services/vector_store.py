import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.config import get_settings
from app.services.embeddings import get_embedding_model

logger = logging.getLogger(__name__)

COLLECTION_NAME = "codebase_chunks"


def _metadata(chunk: dict[str, Any], repository_id: str) -> dict[str, Any]:
    return {
        "repository_id": repository_id,
        "file_path": chunk["file_path"],
        "chunk_index": chunk["chunk_index"],
    }


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    settings = get_settings()
    path = Path(settings["chroma_path"])
    path.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=str(path),
    )


def add_chunks(repository_id: str, chunks: list[dict[str, Any]]) -> int:
    if not repository_id:
        raise ValueError("repository_id is required.")
    if not chunks:
        return 0

    documents = [
        Document(
            page_content=chunk["content"],
            metadata=_metadata(chunk, repository_id),
        )
        for chunk in chunks
    ]
    ids = [
        f"{repository_id}:{chunk['file_path']}:{chunk['chunk_index']}"
        for chunk in chunks
    ]
    get_vector_store().add_documents(documents, ids=ids)
    logger.info("Stored %d chunks for repository %s", len(documents), repository_id)
    return len(documents)


def search_chunks(
    repository_id: str,
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    if not repository_id:
        raise ValueError("repository_id is required.")
    if not query.strip():
        raise ValueError("query must be a non-empty string.")
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    results = get_vector_store().similarity_search_with_score(
        query,
        k=top_k,
        filter={"repository_id": repository_id},
    )
    return [
        {
            "content": document.page_content,
            "file_path": document.metadata["file_path"],
            "chunk_index": document.metadata["chunk_index"],
            "score": score,
        }
        for document, score in results
    ]


def delete_repository(repository_id: str) -> None:
    if not repository_id:
        raise ValueError("repository_id is required.")

    get_vector_store().delete(where={"repository_id": repository_id})
    logger.info("Deleted vector data for repository %s", repository_id)
