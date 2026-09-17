import pytest

from app.services import embeddings


class FakeEmbeddingModel:
    def __init__(self):
        self.calls = []

    def encode(self, texts, **kwargs):
        self.calls.append((texts, kwargs))
        return [[float(index), 1.0] for index, _ in enumerate(texts)]


@pytest.fixture
def fake_model(monkeypatch):
    model = FakeEmbeddingModel()
    embeddings.get_embedding_model.cache_clear()
    monkeypatch.setattr(embeddings, "get_embedding_model", lambda: model)
    return model


def test_embed_documents_returns_one_vector_per_document(fake_model):
    result = embeddings.embed_documents(["def login():", "class User:"])

    assert result == [[0.0, 1.0], [1.0, 1.0]]
    assert fake_model.calls[0][0] == ["def login():", "class User:"]
    assert fake_model.calls[0][1]["normalize_embeddings"] is True


def test_embed_query_uses_search_prefix(fake_model):
    result = embeddings.embed_query("where is login defined?")

    assert result == [0.0, 1.0]
    assert fake_model.calls[0][0] == [
        "Represent this sentence for searching relevant passages: where is login defined?"
    ]


@pytest.mark.parametrize("value", [[], [""], ["   "], [None]])
def test_embed_documents_rejects_empty_values(fake_model, value):
    with pytest.raises(ValueError):
        embeddings.embed_documents(value)


def test_embed_query_rejects_empty_value(fake_model):
    with pytest.raises(ValueError):
        embeddings.embed_query(" ")
