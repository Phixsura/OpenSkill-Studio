from app.services.app_marketplace_app_app_text_diff import compute_text_diff

def test_diff():
    r = compute_text_diff(old="The quick brown fox", new="The quick red fox jumps")
    assert "red" in r["added"]
    assert "jumps" in r["added"]
    assert "brown" in r["removed"]
    assert r["has_changes"]

def test_identical():
    r = compute_text_diff(old="hello world", new="hello world")
    assert not r["has_changes"]
    assert r["similarity_pct"] == 100.0

def test_xss():
    r = compute_text_diff(old="", new="<script>alert(1)</script>")
    assert "<script>" not in r["added"][0]
