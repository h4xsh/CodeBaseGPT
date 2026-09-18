import pytest

from app.services import embeddings


class FakeEmbeddingModel:
    def __init__(self):
        self.calls = []

    def embed_documents(self, texts):
        self.calls.append(("documents", texts))
        return [[float(index), 1.0] for index, _ in enumerate(texts)]

    def embed_query(self, query):
        self.calls.append(("query", query))
        return [0.0, 1.0]


@pytest.fixture
def fake_model(monkeypatch):
    model = FakeEmbeddingModel()
    embeddings.get_embedding_model.cache_clear()
    monkeypatch.setattr(embeddings, "get_embedding_model", lambda: model)
    return model


def test_embed_documents_returns_one_vector_per_document(fake_model):
    result = embeddings.embed_documents(["def login():", "class User:"])

    assert result == [[0.0, 1.0], [1.0, 1.0]]
    assert fake_model.calls[0] == ("documents", ["def login():", "class User:"])


def test_embed_query_uses_search_prefix(fake_model):
    result = embeddings.embed_query("where is login defined?")

    assert result == [0.0, 1.0]
    assert fake_model.calls[0] == (
        "query",
        "Represent this sentence for searching relevant passages: where is login defined?",
    )


def test_embed_documents_returns_empty_for_empty_batch(fake_model):
    assert embeddings.embed_documents([]) == []


@pytest.mark.parametrize("value", [[""], ["   "], [None]])
def test_embed_documents_rejects_empty_values(fake_model, value):
    with pytest.raises(ValueError):
        embeddings.embed_documents(value)


def test_embed_query_rejects_empty_value(fake_model):
    with pytest.raises(ValueError):
        embeddings.embed_query(" ")
