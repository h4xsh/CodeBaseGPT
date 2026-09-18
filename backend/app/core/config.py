from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@lru_cache(maxsize=1)
def get_settings():
    import os

    return {
        "app_name": "CodebaseGPT",
        "app_version": "0.1.0",
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "qwen3:8b"),
        "groq_api_key": os.getenv("GROQ_API_KEY", ""),
        "groq_model": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        "chroma_path": os.getenv("CHROMA_PATH", str(BASE_DIR.parent / "data" / ".chroma_db")),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),
        "repo_storage_path": os.getenv(
            "REPO_STORAGE_PATH",
            str(BASE_DIR.parent / "data" / "repositories"),
        ),
        "max_file_size": int(os.getenv("MAX_FILE_SIZE", str(1_000_000))),
    }
