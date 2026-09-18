from types import SimpleNamespace

import pytest

from app.services import vector_store


class FakeCollection:
    def __init__(self):
        self.deleted = []

    def delete(self, **kwargs):
        self.deleted.append(kwargs)


class FakeStore:
    def __init__(self):
        self.added = []
        self.deleted = []

    def add_documents(self, documents, ids):
        self.added.append((documents, ids))

    def similarity_search_with_score(self, query, k, filter):
        return [
            (
                SimpleNamespace(
                    page_content="def login(): pass",
                    metadata={"file_path": "auth.py", "chunk_index": 0},
                ),
                0.12,
            )
        ]

    def delete(self, **kwargs):
        self.deleted.append(kwargs)


@pytest.fixture
def fake_store(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr(vector_store, "get_vector_store", lambda: store)
    return store


def test_add_chunks_stores_documents_and_metadata(fake_store):
    count = vector_store.add_chunks(
        "repo_demo",
        [{"content": "code", "file_path": "main.py", "chunk_index": 0}],
    )

    assert count == 1
    documents, ids = fake_store.added[0]
    assert documents[0].page_content == "code"
    assert documents[0].metadata["repository_id"] == "repo_demo"
    assert ids == ["repo_demo:main.py:0"]


def test_search_chunks_returns_source_metadata(fake_store):
    results = vector_store.search_chunks("repo_demo", "where is login?", top_k=5)

    assert results == [
        {
            "content": "def login(): pass",
            "file_path": "auth.py",
            "chunk_index": 0,
            "score": 0.12,
        }
    ]


def test_delete_repository_filters_by_repository(fake_store):
    vector_store.delete_repository("repo_demo")

    assert fake_store.deleted == [{"where": {"repository_id": "repo_demo"}}]


@pytest.mark.parametrize(
    "operation",
    [
        lambda: vector_store.add_chunks("", []),
        lambda: vector_store.search_chunks("", "query"),
        lambda: vector_store.search_chunks("repo", ""),
        lambda: vector_store.search_chunks("repo", "query", top_k=0),
        lambda: vector_store.delete_repository(""),
    ],
)
def test_vector_store_rejects_invalid_input(operation):
    with pytest.raises(ValueError):
        operation()
