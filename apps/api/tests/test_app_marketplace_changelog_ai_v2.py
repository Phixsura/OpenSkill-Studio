from app.services.app_marketplace_changelog_ai_v2 import generate_user_changelog, summarize_changelog

def test_end_user():
    changes = [{"type": "feat", "description": "Add dark mode", "user_facing_description": "Dark mode is here!"},
               {"type": "refactor", "description": "Clean up code"}]
    r = generate_user_changelog(changes=changes, audience="end_user")
    assert r["count"] == 1
    assert "Dark mode is here!" in r["entries"][0]

def test_developer():
    changes = [{"type": "feat", "description": "API"}, {"type": "refactor", "description": "Cleanup"}]
    r = generate_user_changelog(changes=changes, audience="developer")
    assert r["count"] == 2

def test_summarize():
    changes = [{"type": "feat"}, {"type": "feat"}, {"type": "fix"}, {"type": "perf"}]
    s = summarize_changelog(changes=changes)
    assert "2 new features" in s["headline"]
    assert "1 bug fix" in s["headline"]
    assert s["total_changes"] == 4
