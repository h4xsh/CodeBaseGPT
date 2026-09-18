import logging
from collections.abc import Iterator
from functools import lru_cache

from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_primary_llm() -> ChatGroq:
    settings = get_settings()
    return ChatGroq(
        api_key=settings["groq_api_key"],
        model=settings["groq_model"],
        temperature=0,
        reasoning_format="hidden",
    )


@lru_cache(maxsize=1)
def get_fallback_llm() -> ChatOllama:
    settings = get_settings()
    return ChatOllama(
        base_url=settings["ollama_base_url"],
        model=settings["ollama_model"],
        temperature=0,
    )


def _content(response) -> str:
    content = response.content if hasattr(response, "content") else ""
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("The model returned an empty response.")
    return content.strip()


def generate_answer(prompt: str) -> dict[str, str]:
    if not prompt.strip():
        raise ValueError("prompt must be a non-empty string.")

    settings = get_settings()
    if settings.get("groq_api_key", "").strip():
        try:
            answer = _content(get_primary_llm().invoke(prompt))
            logger.info("Received response from Groq model %s", settings["groq_model"])
            return {"answer": answer, "model": settings["groq_model"]}
        except Exception as primary_exc:
            logger.warning("Groq generation failed; using Ollama fallback: %s", primary_exc)
    else:
        logger.info("GROQ_API_KEY is not configured; using Ollama fallback.")

    try:
        answer = _content(get_fallback_llm().invoke(prompt))
        logger.info("Received response from Ollama fallback %s", settings["ollama_model"])
        return {"answer": answer, "model": settings["ollama_model"]}
    except Exception as fallback_exc:
        logger.error("Ollama fallback generation failed: %s", fallback_exc)
        raise RuntimeError(
            "Could not generate an answer from Groq or the Ollama fallback."
        ) from fallback_exc


def stream_answer(prompt: str) -> Iterator[dict[str, str]]:
    """Stream Groq output and fall back to Ollama if Groq fails."""
    if not prompt.strip():
        raise ValueError("prompt must be a non-empty string.")

    settings = get_settings()
    if settings.get("groq_api_key", "").strip():
        yielded_content = False
        try:
            for chunk in get_primary_llm().stream(prompt):
                content = chunk.content if hasattr(chunk, "content") else ""
                if isinstance(content, str) and content:
                    yielded_content = True
                    yield {"content": content, "model": settings["groq_model"]}
            return
        except Exception as primary_exc:
            if yielded_content:
                logger.error("Groq streaming stopped after producing partial output: %s", primary_exc)
                raise RuntimeError("Groq streaming stopped unexpectedly.") from primary_exc
            logger.warning("Groq streaming failed before output; using Ollama fallback: %s", primary_exc)
    else:
        logger.info("GROQ_API_KEY is not configured; using Ollama fallback stream.")

    try:
        for chunk in get_fallback_llm().stream(prompt):
            content = chunk.content if hasattr(chunk, "content") else ""
            if isinstance(content, str) and content:
                yield {"content": content, "model": settings["ollama_model"]}
    except Exception as fallback_exc:
        logger.error("Ollama fallback streaming failed: %s", fallback_exc)
        raise RuntimeError(
            "Could not generate an answer from Groq or the Ollama fallback."
        ) from fallback_exc
