from app.services.github import get_repository_name, parse_github_url


def test_parse_github_url_valid():
    owner, repo = parse_github_url("https://github.com/microsoft/vscode")
    assert owner == "microsoft"
    assert repo == "vscode"


def test_parse_github_url_invalid():
    try:
        parse_github_url("https://example.com/owner/repo")
        assert False, "Expected ValueError for non-GitHub URL"
    except ValueError:
        pass


def test_get_repository_name():
    assert get_repository_name("https://github.com/microsoft/vscode") == "vscode"
