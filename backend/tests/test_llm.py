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


def test_generate_answer_returns_model_text(monkeypatch):
    model = FakeLLM(response=type("Response", (), {"content": "  grounded answer  "})())
    monkeypatch.setattr(llm, "get_llm", lambda: model)

    assert llm.generate_answer("Use this repository context.") == "grounded answer"
    assert model.prompts == ["Use this repository context."]


def test_generate_answer_reports_ollama_errors(monkeypatch):
    monkeypatch.setattr(llm, "get_llm", lambda: FakeLLM(error=ConnectionError()))

    with pytest.raises(RuntimeError, match="Ollama"):
        llm.generate_answer("Answer this.")


def test_generate_answer_rejects_empty_prompt(monkeypatch):
    monkeypatch.setattr(llm, "get_llm", lambda: FakeLLM())

    with pytest.raises(ValueError):
        llm.generate_answer(" ")
