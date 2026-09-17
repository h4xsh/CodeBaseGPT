import pytest

from app.services.chunker import chunk_file, chunk_files, chunk_text


def test_large_text_is_split_with_overlap():
    chunks = chunk_text("abcdefghij", chunk_size=5, chunk_overlap=2)

    assert chunks == ["abcde", "defgh", "ghij"]


def test_chunk_metadata_is_preserved():
    chunks = chunk_file(
        {"path": "src/auth.py", "content": "abcdefghij"},
        chunk_size=4,
        chunk_overlap=0,
    )

    assert chunks == [
        {"content": "abcd", "file_path": "src/auth.py", "chunk_index": 0},
        {"content": "efgh", "file_path": "src/auth.py", "chunk_index": 1},
        {"content": "ij", "file_path": "src/auth.py", "chunk_index": 2},
    ]


def test_chunk_files_combines_files():
    chunks = chunk_files(
        [
            {"path": "a.py", "content": "1234"},
            {"path": "b.py", "content": "5678"},
        ],
        chunk_size=4,
        chunk_overlap=0,
    )

    assert [chunk["file_path"] for chunk in chunks] == ["a.py", "b.py"]


@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap"),
    [(0, 0), (4, -1), (4, 4), (4, 5)],
)
def test_invalid_chunk_settings_are_rejected(chunk_size, chunk_overlap):
    with pytest.raises(ValueError):
        chunk_text("content", chunk_size=chunk_size, chunk_overlap=chunk_overlap)
