import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from app.core.config import get_settings


def _remove_directory(path: Path):
    if not path.exists():
        return

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            file_path = Path(root) / name
            try:
                os.chmod(file_path, 0o666)
                file_path.unlink()
            except PermissionError:
                pass
        for name in dirs:
            dir_path = Path(root) / name
            try:
                os.chmod(dir_path, 0o777)
                dir_path.rmdir()
            except PermissionError:
                pass

    try:
        path.rmdir()
    except PermissionError:
        shutil.rmtree(path, ignore_errors=True)


def parse_github_url(github_url: str):
    parsed = urlparse(github_url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("GitHub URL must start with http:// or https://")

    if parsed.netloc.lower() != "github.com":
        raise ValueError("Only public GitHub repository URLs are supported.")

    path = parsed.path.strip("/")
    if not path:
        raise ValueError("GitHub URL must include owner and repository name.")

    if path.endswith(".git"):
        path = path[:-4]

    parts = path.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("GitHub URL must be in the format https://github.com/owner/repository")

    return parts[0], parts[1]


def get_repository_name(github_url: str) -> str:
    _, repo_name = parse_github_url(github_url)
    return repo_name


def clone_repository(github_url: str, storage_root: str | Path | None = None) -> str:
    owner, repo_name = parse_github_url(github_url)
    root = Path(storage_root) if storage_root is not None else Path(get_settings()["repo_storage_path"])
    root.mkdir(parents=True, exist_ok=True)

    repo_dir = root / f"{owner}__{repo_name}"
    if repo_dir.exists():
        _remove_directory(repo_dir)

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", github_url, str(repo_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Git is not installed or is not available on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        error = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise RuntimeError(f"Repository cloning failed: {error}") from exc

    return str(repo_dir.resolve())
