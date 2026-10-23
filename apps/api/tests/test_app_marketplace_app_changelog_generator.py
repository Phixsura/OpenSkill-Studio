from app.services.app_marketplace_app_changelog_generator import parse_commits, render_changelog

def test_parse():
    commits = ["feat: add dark mode", "fix(ui): button alignment", "feat!: new API surface"]
    r = parse_commits(commits=commits)
    assert r["total"] == 3
    assert "add dark mode" in r["groups"]["Features"]
    assert r["has_breaking"]
    assert "new API surface" in r["breaking_changes"]

def test_render():
    parsed = parse_commits(commits=["feat: login page", "fix: typo"])
    md = render_changelog(version="1.2.0", date="2026-10-23", parsed=parsed)
    assert "## 1.2.0 (2026-10-23)" in md
    assert "- login page" in md
    assert "- typo" in md
