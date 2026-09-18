import logging
from functools import lru_cache
from typing import Iterable

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 2_000
DEFAULT_CHUNK_OVERLAP = 200


@lru_cache(maxsize=16)
def get_text_splitter(
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split text with LangChain while preserving source order and overlap."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")
    if not text:
        return []

    return get_text_splitter(chunk_size, chunk_overlap).split_text(text)


def chunk_file(
    file: dict[str, str],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict[str, str | int]]:
    """Chunk one loaded file while preserving its source path and index."""
    file_path = file.get("path")
    content = file.get("content")
    if not file_path or content is None:
        raise ValueError("Each file must contain non-empty 'path' and 'content' fields.")

    documents = get_text_splitter(chunk_size, chunk_overlap).create_documents(
        [content],
        metadatas=[{"file_path": file_path}],
    )
    return [
        {
            "content": document.page_content,
            "file_path": document.metadata["file_path"],
            "chunk_index": index,
        }
        for index, document in enumerate(documents)
    ]


def chunk_files(
    files: Iterable[dict[str, str]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict[str, str | int]]:
    """Chunk all loaded repository files in their supplied order."""
    file_list = list(files)
    chunks = [
        chunk
        for file in file_list
        for chunk in chunk_file(file, chunk_size, chunk_overlap)
    ]

    logger.info("Created %d chunks from %d files", len(chunks), len(file_list))
    return chunks
