from app.services.app_marketplace_app_app_app_app_app_app_app_change_diff import analyze_diff, summarize_diffs

def test_diff():
    r = analyze_diff(
        {"a": 1, "b": 2, "c": 3},
        {"a": 1, "b": 5, "d": 4})
    assert r["added"] == {"d": 4}
    assert r["removed"] == {"c": 3}
    assert "b" in r["changed"]
    assert r["risk"] == "high"

def test_no_change():
    r = analyze_diff({"x": 1}, {"x": 1})
    assert r["total_changes"] == 0
    assert r["risk"] == "none"

def test_summary():
    diffs = [analyze_diff({"a": 1}, {"a": 2}), analyze_diff({"b": 1}, {"b": 1, "c": 2})]
    r = summarize_diffs(diffs)
    assert r["total_diffs"] == 2
    assert r["high_risk"] == 1
