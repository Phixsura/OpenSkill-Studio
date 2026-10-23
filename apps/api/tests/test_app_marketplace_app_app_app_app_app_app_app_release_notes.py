from app.services.app_marketplace_app_app_app_app_app_app_app_release_notes import generate_release_notes

def test_release_notes():
    commits = [
        "feat(auth): add SSO support",
        "feat(api): new export endpoint",
        "fix(ui): button alignment",
        "fix: typo in error message",
        "docs: update README",
        "chore: bump deps",
        "random commit message",
    ]
    r = generate_release_notes(commits, version="3.2.0", date="2026-10-24")
    assert r["version"] == "3.2.0"
    assert r["total_commits"] == 7
    feat_section = next(s for s in r["sections"] if s["category"] == "feat")
    assert feat_section["count"] == 2
    assert len(r["uncategorized"]) == 1
    assert not r["has_breaking"]
