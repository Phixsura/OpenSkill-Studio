from app.services.app_marketplace_app_app_app_app_app_app_app_diff_util import compute_diff

def test_diff():
    old = "line1\nline2\nline3"
    new = "line1\nmodified\nline3\nline4"
    r = compute_diff(old, new)
    assert r["added"] >= 1
    assert r["removed"] >= 1
    assert r["summary"].startswith("+")
    assert any(l["type"] == "unchanged" for l in r["lines"])
    assert any(l["type"] == "added" for l in r["lines"])

def test_identical():
    r = compute_diff("same\ntext", "same\ntext")
    assert r["total_changes"] == 0
    assert r["unchanged"] == 2
