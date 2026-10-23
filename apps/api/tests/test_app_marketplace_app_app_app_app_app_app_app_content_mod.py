from app.services.app_marketplace_app_app_app_app_app_app_app_content_mod import moderate_text, moderate_batch

def test_clean():
    r = moderate_text("Hello, this is a normal message")
    assert r["action"] == "approve"
    assert r["flag_count"] == 0

def test_blocked():
    r = moderate_text("This is a spam message <script>alert(1)</script>")
    assert r["action"] == "reject"
    assert r["blocked"]

def test_warning():
    r = moderate_text("Click here for amazing deals")
    assert r["action"] == "review"

def test_batch():
    r = moderate_batch(["Good text", "spam content", "Click here now"])
    assert r["total"] == 3
    assert r["approved"] == 1
    assert r["rejected"] == 1
    assert r["review"] == 1
