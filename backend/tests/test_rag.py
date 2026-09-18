from app.services import rag


def test_answer_question_retrieves_context_and_returns_sources(monkeypatch):
    captured = {}
    chunks = [
        {
            "content": "def login(): return token",
            "file_path": "auth.py",
            "chunk_index": 0,
            "score": 0.1,
        }
    ]

    def fake_search(repository_id, query, top_k):
        captured["search"] = (repository_id, query, top_k)
        return chunks

    def fake_generate(prompt):
        captured["prompt"] = prompt
        return "Authentication is implemented in auth.py."

    monkeypatch.setattr(rag, "search_chunks", fake_search)
    monkeypatch.setattr(rag, "generate_answer", fake_generate)

    result = rag.answer_question(
        "repo_demo",
        "How does authentication work?",
        [{"role": "user", "content": "Where is login?"}],
    )

    assert captured["search"] == ("repo_demo", "How does authentication work?", 5)
    assert "auth.py" in captured["prompt"]
    assert "Where is login?" in captured["prompt"]
    assert result == {
        "answer": "Authentication is implemented in auth.py.",
        "sources": [
            {
                "file_path": "auth.py",
                "snippet": "def login(): return token",
                "chunk_index": 0,
                "score": 0.1,
            }
        ],
    }


def test_answer_question_handles_missing_context(monkeypatch):
    monkeypatch.setattr(rag, "search_chunks", lambda *args, **kwargs: [])
    monkeypatch.setattr(rag, "generate_answer", lambda prompt: "I do not have enough information.")

    result = rag.answer_question("repo_demo", "What is missing?")

    assert result["sources"] == []
