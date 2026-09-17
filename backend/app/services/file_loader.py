import logging
import os
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".html",
    ".css",
    ".md",
    ".json",
}

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "coverage",
    ".next",
    "target",
    "bin",
    "obj",
}

IGNORED_FILE_NAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}


def is_ignored_file(path: Path) -> bool:
    name = path.name
    return name in IGNORED_FILE_NAMES or name == ".env" or name.startswith(".env.")


def discover_files(
    repository_path: str | Path,
    max_file_size: int | None = None,
) -> list[Path]:
    root = Path(repository_path)
    if not root.is_dir():
        raise ValueError(f"Repository path does not exist or is not a directory: {root}")

    if max_file_size is None:
        max_file_size = get_settings()["max_file_size"]

    discovered: list[Path] = []
    for current_root, directories, file_names in os.walk(root, topdown=True, followlinks=False):
        directories[:] = sorted(
            directory for directory in directories if directory not in IGNORED_DIRECTORIES
        )

        for file_name in sorted(file_names):
            path = Path(current_root) / file_name
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS or is_ignored_file(path):
                continue

            try:
                if path.stat().st_size > max_file_size:
                    logger.info("Skipping oversized file: %s", path)
                    continue
            except OSError as exc:
                logger.warning("Skipping unreadable file %s: %s", path, exc)
                continue

            discovered.append(path)

    logger.info("Discovered %d supported files in %s", len(discovered), root)
    return discovered


def load_repository_files(
    repository_path: str | Path,
    max_file_size: int | None = None,
) -> list[dict[str, str]]:
    files = []
    root = Path(repository_path)

    for path in discover_files(root, max_file_size=max_file_size):
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            logger.warning("Skipping unreadable text file %s: %s", path, exc)
            continue

        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "content": content,
            }
        )

    logger.info("Loaded %d repository files from %s", len(files), root)
    return files
