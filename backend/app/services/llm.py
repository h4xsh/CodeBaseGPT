import logging
from functools import lru_cache

from langchain_ollama import ChatOllama

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm() -> ChatOllama:
    settings = get_settings()
    logger.info("Connecting to Ollama model: %s", settings["ollama_model"])
    return ChatOllama(
        base_url=settings["ollama_base_url"],
        model=settings["ollama_model"],
        temperature=0,
    )


def generate_answer(prompt: str) -> str:
    if not prompt.strip():
        raise ValueError("prompt must be a non-empty string.")

    try:
        response = get_llm().invoke(prompt)
    except Exception as exc:
        logger.error("Ollama generation failed: %s", exc)
        raise RuntimeError(
            "Could not generate an answer. Ensure Ollama is running and qwen3:8b is available."
        ) from exc

    answer = response.content
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("Ollama returned an empty response.")

    logger.info("Received Ollama response")
    return answer.strip()
