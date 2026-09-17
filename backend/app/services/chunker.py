import logging
from typing import Iterable

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 2_000
DEFAULT_CHUNK_OVERLAP = 200


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

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_text(text)


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

    chunks = [
        {
            "content": content_chunk,
            "file_path": file_path,
            "chunk_index": index,
        }
        for index, content_chunk in enumerate(
            chunk_text(content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        )
    ]
    return chunks


def chunk_files(
    files: Iterable[dict[str, str]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict[str, str | int]]:
    """Chunk all loaded repository files in their supplied order."""
    file_list = list(files)
    chunks = []
    for file in file_list:
        chunks.extend(
            chunk_file(
                file,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        )

    logger.info("Created %d chunks from %d files", len(chunks), len(file_list))
    return chunks
