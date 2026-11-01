from app.services.app_marketplace_app_release_notes_ai import generate_release_notes

def test_generate():
    commits = ["feat: add dark mode", "fix: login crash", "perf: optimize queries",
               "docs: update README", "chore: update deps"]
    r = generate_release_notes(version="2.0.0", commits=commits, app_name="MyApp")
    assert r["has_features"]
    assert r["has_fixes"]
    assert r["section_count"] >= 4
    assert "# MyApp v2.0.0" in r["markdown"]
    assert "- add dark mode" in r["markdown"]

def test_no_conventional():
    commits = ["random commit message", "another one"]
    r = generate_release_notes(version="1.0", commits=commits, app_name="App")
    assert r["section_count"] == 1  # all in Other
