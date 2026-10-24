from app.services.app_marketplace_app_app_app_app_app_app_app_changelog_gen import parse_commits, generate_changelog

def test_parse():
    commits = parse_commits(["feat(auth): add OAuth", "fix: typo", "random message"])
    assert commits[0]["type"] == "feat"
    assert commits[0]["scope"] == "auth"
    assert commits[1]["type"] == "fix"
    assert commits[2]["type"] == "other"

def test_changelog():
    commits = [
        {"type": "feat", "scope": "", "description": "New dashboard"},
        {"type": "fix", "scope": "", "description": "Login bug"},
    ]
    r = generate_changelog("2.0.0", commits)
    assert "## 2.0.0" in r["markdown"]
    assert "New dashboard" in r["markdown"]
    assert r["commit_count"] == 2
