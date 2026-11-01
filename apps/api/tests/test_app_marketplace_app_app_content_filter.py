from app.services.app_marketplace_app_app_content_filter import check_content

def test_safe():
    r = check_content(text="This is a great app!")
    assert r["safe"]
    assert r["flag_count"] == 0

def test_flagged():
    r = check_content(text="This is spam content with phishing links")
    assert not r["safe"]
    assert r["flag_count"] == 2
    assert r["max_severity"] == "critical"
    assert "****" in r["cleaned"]

def test_xss():
    r = check_content(text="<script>alert(1)</script>")
    assert "<script>" not in r["original"]
