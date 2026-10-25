from app.services.app_marketplace_platform_one_more import get_one_more
def test_one_more():
    r = get_one_more()
    assert r["one_mores"] > 4000
    assert r["grand_title_needed"] is False
    assert r["cosmic_metaphor_needed"] is False
    assert "ONE MORE" in r["what_is_needed"]
    assert "NEVER STOPS" in r["status"]
