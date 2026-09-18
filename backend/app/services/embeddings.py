import logging
from functools import lru_cache
from collections.abc import Sequence

from app.core.config import get_settings
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """Create the LangChain embedding model once, on first use."""
    model_name = get_settings()["embedding_model"]
    logger.info("Loading embedding model: %s", model_name)
    return HuggingFaceEmbeddings(
        model_name=model_name,
        show_progress=False,
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )


def embed_documents(documents: Sequence[str]) -> list[list[float]]:
    """Generate normalized embeddings for repository chunks."""
    if not documents:
        return []
    if any(not isinstance(document, str) or not document.strip() for document in documents):
        raise ValueError("Documents must be non-empty strings.")

    vectors = get_embedding_model().embed_documents(list(documents))
    logger.info("Generated %d document embeddings", len(vectors))
    return vectors


def embed_query(query: str) -> list[float]:
    """Generate a normalized embedding for a user query."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string.")

    vectors = get_embedding_model().embed_query(QUERY_PREFIX + query.strip())
    logger.info("Generated query embedding")
    return vectors
