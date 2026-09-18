import pytest

from app.services import llm


class FakeLLM:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return self.response

    def stream(self, prompt):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return [type("Chunk", (), {"content": part})() for part in ("first ", "second")]


def test_generate_answer_uses_groq(monkeypatch):
    model = FakeLLM(response=type("Response", (), {"content": "  grounded answer  "})())
    monkeypatch.setattr(llm, "get_primary_llm", lambda: model)
    monkeypatch.setattr(llm, "get_settings", lambda: {
        "groq_api_key": "test-key",
        "groq_model": "openai/gpt-oss-120b",
        "ollama_model": "qwen3:8b",
    })

    assert llm.generate_answer("Use this repository context.") == {
        "answer": "grounded answer",
        "model": "openai/gpt-oss-120b",
    }
    assert model.prompts == ["Use this repository context."]


def test_generate_answer_falls_back_to_ollama(monkeypatch):
    monkeypatch.setattr(llm, "get_primary_llm", lambda: FakeLLM(error=ConnectionError()))
    monkeypatch.setattr(
        llm,
        "get_fallback_llm",
        lambda: FakeLLM(response=type("Response", (), {"content": "fallback answer"})()),
    )
    monkeypatch.setattr(llm, "get_settings", lambda: {
        "groq_api_key": "test-key",
        "groq_model": "openai/gpt-oss-120b",
        "ollama_model": "qwen3:8b",
    })

    assert llm.generate_answer("Answer this.") == {
        "answer": "fallback answer",
        "model": "qwen3:8b",
    }


def test_generate_answer_rejects_empty_prompt(monkeypatch):
    with pytest.raises(ValueError):
        llm.generate_answer(" ")


def test_stream_answer_yields_model_chunks(monkeypatch):
    model = FakeLLM()
    monkeypatch.setattr(llm, "get_primary_llm", lambda: model)
    monkeypatch.setattr(llm, "get_settings", lambda: {
        "groq_api_key": "test-key",
        "groq_model": "openai/gpt-oss-120b",
        "ollama_model": "qwen3:8b",
    })

    assert list(llm.stream_answer("Answer this.")) == [
        {"content": "first ", "model": "openai/gpt-oss-120b"},
        {"content": "second", "model": "openai/gpt-oss-120b"},
    ]


def test_stream_answer_falls_back_before_first_groq_chunk(monkeypatch):
    monkeypatch.setattr(llm, "get_primary_llm", lambda: FakeLLM(error=ConnectionError()))
    monkeypatch.setattr(llm, "get_fallback_llm", FakeLLM)
    monkeypatch.setattr(llm, "get_settings", lambda: {
        "groq_api_key": "test-key",
        "groq_model": "openai/gpt-oss-120b",
        "ollama_model": "qwen3:8b",
    })

    assert list(llm.stream_answer("Answer this.")) == [
        {"content": "first ", "model": "qwen3:8b"},
        {"content": "second", "model": "qwen3:8b"},
    ]
