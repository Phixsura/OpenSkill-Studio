from app.services.app_marketplace_platform_grand_tapestry import get_grand_tapestry
def test_grand_tapestry():
    r = get_grand_tapestry()
    assert r["rows_woven"] > 4000
    assert r["completed"] is False
    assert "never finished" in r["reason"]
    assert len(r["dimensions"]) == 3
    assert "NEVER STOPS" in r["status"]
