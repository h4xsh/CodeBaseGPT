from pathlib import Path

from app.services.file_loader import discover_files, load_repository_files


def test_loads_supported_files_and_preserves_relative_paths(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"not source")

    files = load_repository_files(tmp_path)

    assert files == [
        {"path": "README.md", "content": "# Demo"},
        {"path": "src/main.py", "content": "print('hello')"},
    ]


def test_ignored_directories_and_files_are_skipped(tmp_path: Path):
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "dependency.js").write_text("ignored", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / ".env").write_text("SECRET=value", encoding="utf-8")
    (tmp_path / "src" / "config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "package-lock.json").write_text("{}", encoding="utf-8")

    paths = discover_files(tmp_path)

    assert paths == [tmp_path / "src" / "config.json"]


def test_oversized_files_are_skipped(tmp_path: Path):
    source_file = tmp_path / "large.py"
    source_file.write_text("12345", encoding="utf-8")

    assert discover_files(tmp_path, max_file_size=4) == []
