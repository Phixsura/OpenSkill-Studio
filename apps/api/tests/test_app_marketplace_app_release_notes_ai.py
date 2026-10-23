from app.services.app_marketplace_app_release_notes_ai import categorize_commits, generate_release_notes, render_release_notes_md

def test_categorize():
    commits = [{"message": "feat: add dark mode"}, {"message": "fix: login bug"},
               {"message": "refactor: cleanup"}, {"message": "update readme"}]
    c = categorize_commits(commits=commits)
    assert len(c["features"]) == 1
    assert len(c["fixes"]) == 1
    assert len(c["improvements"]) == 1
    assert len(c["other"]) == 1

def test_generate():
    commits = [{"message": "feat: add webhooks"}, {"message": "fix: auth crash"}]
    r = generate_release_notes(version="2.0.0", commits=commits, breaking=["Removed v1 API"])
    assert r["total_commits"] == 2
    assert len(r["sections"]) == 3  # breaking + features + fixes

def test_render():
    notes = generate_release_notes(version="1.0", commits=[{"message": "feat: initial"}])
    md = render_release_notes_md(notes=notes)
    assert "# Release 1.0" in md
    assert "New Features" in md
