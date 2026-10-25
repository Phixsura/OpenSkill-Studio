from app.services.app_marketplace_changelog_generator import (
    parse_commit, generate_changelog,
)


def test_parse_simple():
    c = parse_commit("feat: add dark mode")
    assert c is not None
    assert c.type == "feat"
    assert c.description == "add dark mode"
    assert c.scope == ""
    assert c.breaking is False


def test_parse_with_scope():
    c = parse_commit("fix(auth): resolve token expiry")
    assert c.type == "fix"
    assert c.scope == "auth"
    assert c.description == "resolve token expiry"


def test_parse_breaking():
    c = parse_commit("feat!: remove legacy API")
    assert c.breaking is True


def test_parse_breaking_body():
    c = parse_commit("feat: new API\n\nBREAKING CHANGE: old API removed")
    assert c.breaking is True


def test_parse_invalid():
    assert parse_commit("random message") is None
    assert parse_commit("") is None


def test_generate_changelog():
    commits = [
        parse_commit("feat: add search", "abc1"),
        parse_commit("feat(ui): new dashboard", "abc2"),
        parse_commit("fix: memory leak", "abc3"),
        parse_commit("docs: update README", "abc4"),
        parse_commit("feat!: remove v1 API", "abc5"),
    ]
    cl = generate_changelog("2.0.0", commits, "2026-10-26")
    assert "## 2.0.0 (2026-10-26)" in cl
    assert "Breaking Changes" in cl
    assert "remove v1 API" in cl
    assert "✨ Features" in cl
    assert "add search" in cl
    assert "🐛 Bug Fixes" in cl
    assert "memory leak" in cl


def test_empty_changelog():
    cl = generate_changelog("1.0.0", [])
    assert "## 1.0.0" in cl
