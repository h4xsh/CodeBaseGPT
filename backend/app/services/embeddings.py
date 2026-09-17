import logging
from functools import lru_cache
from typing import Any, Sequence

from app.core.config import get_settings

logger = logging.getLogger(__name__)

QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the local embedding model once, on first use."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "SentenceTransformers is not installed. Install backend requirements first."
        ) from exc

    model_name = get_settings()["embedding_model"]
    logger.info("Loading embedding model: %s", model_name)
    return SentenceTransformer(model_name)


def _encode(model: Any, texts: Sequence[str]) -> list[list[float]]:
    vectors = model.encode(
        list(texts),
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return vectors.tolist()


def embed_documents(documents: Sequence[str]) -> list[list[float]]:
    """Generate normalized embeddings for repository chunks."""
    if not documents:
        return []
    if any(not isinstance(document, str) or not document.strip() for document in documents):
        raise ValueError("Documents must be non-empty strings.")

    vectors = _encode(get_embedding_model(), documents)
    logger.info("Generated %d document embeddings", len(vectors))
    return vectors


def embed_query(query: str) -> list[float]:
    """Generate a normalized embedding for a user query."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string.")

    vectors = _encode(get_embedding_model(), [QUERY_PREFIX + query.strip()])
    logger.info("Generated query embedding")
    return vectors[0]
