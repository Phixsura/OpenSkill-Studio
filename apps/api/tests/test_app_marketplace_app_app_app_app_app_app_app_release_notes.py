from app.services.app_marketplace_app_app_app_app_app_app_app_release_notes import generate_notes, diff_releases

def test_generate():
    r = generate_notes("3.0.0", [
        {"title": "Add dark mode", "label": "feature", "author": "alice"},
        {"title": "Fix login bug", "label": "bugfix", "author": "bob"},
    ], ["alice", "bob"])
    assert r["pr_count"] == 2
    assert r["contributor_count"] == 2
    assert "# Release 3.0.0" in r["markdown"]
    assert "dark mode" in r["markdown"]

def test_diff():
    prev = generate_notes("2.0", [{"title": "x", "author": "a"}], ["a"])
    curr = generate_notes("3.0", [{"title": "x", "author": "a"}, {"title": "y", "author": "b"}], ["a", "b"])
    r = diff_releases(prev, curr)
    assert r["new_prs"] == 1
    assert r["new_contributors"] == 1
