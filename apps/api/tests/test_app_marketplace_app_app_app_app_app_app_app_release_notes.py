from app.services.app_marketplace_app_app_app_app_app_app_app_release_notes import generate_release_notes, compare_releases

def test_generate():
    r = generate_release_notes([
        {"message": "feat: add dark mode"},
        {"message": "fix: login bug"},
        {"message": "BREAKING CHANGE: new API"},
        {"message": "chore: update deps"},
    ], version="2.0.0")
    assert len(r["features"]) == 1
    assert len(r["fixes"]) == 1
    assert r["has_breaking"]

def test_compare():
    v1 = generate_release_notes([], "1.0")
    v2 = generate_release_notes([{"message": "feat: new"}], "2.0")
    r = compare_releases(v1, v2)
    assert r["upgrade_risk"] == "low"
    assert len(r["new_features"]) == 1
