from app.services.app_marketplace_app_app_changelog_generator import parse_commits

def test_parse():
    commits = [
        "feat(auth): add SSO support",
        "fix: resolve login crash",
        "feat!: redesign API endpoints",
        "docs: update README",
        "not a conventional commit",
    ]
    r = parse_commits(commits=commits)
    assert r["total_commits"] == 5
    assert r["parsed"] == 4
    assert len(r["unparsed"]) == 1
    assert r["has_breaking"]
    assert len(r["sections"]) >= 3

def test_empty():
    r = parse_commits(commits=[])
    assert r["total_commits"] == 0
