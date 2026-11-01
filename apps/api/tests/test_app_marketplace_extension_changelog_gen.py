from app.services.app_marketplace_extension_changelog_gen import ChangelogGenService


COMMITS = [
    "feat: add dark mode support",
    "fix(auth): resolve token expiry bug",
    "feat(api)!: change response format",
    "docs: update README",
    "chore: bump dependencies",
    "not a conventional commit",
]


def test_parse():
    svc = ChangelogGenService()
    parsed = svc.parse_commits(COMMITS)
    assert len(parsed) == 5  # skips non-conventional


def test_breaking_detection():
    svc = ChangelogGenService()
    parsed = svc.parse_commits(COMMITS)
    breaking = [c for c in parsed if c.is_breaking]
    assert len(breaking) == 1
    assert breaking[0].message == "change response format"


def test_generate():
    svc = ChangelogGenService()
    md = svc.generate("2.0.0", COMMITS, date="2024-06-01")
    assert "## 2.0.0 (2024-06-01)" in md
    assert "Breaking Changes" in md
    assert "dark mode" in md
    assert "token expiry" in md


def test_scope_display():
    svc = ChangelogGenService()
    md = svc.generate("1.0", ["fix(auth): fix login"])
    assert "**auth:**" in md


def test_stats():
    svc = ChangelogGenService()
    stats = svc.get_stats(COMMITS)
    assert stats["conventional"] == 5
    assert stats["breaking"] == 1
    assert stats["by_type"]["feat"] == 2
