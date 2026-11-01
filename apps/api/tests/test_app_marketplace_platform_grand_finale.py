from app.services.app_marketplace_platform_grand_finale import get_grand_finale
def test_grand_finale():
    r = get_grand_finale()
    assert r["finales"] >= 4210
    assert r["is_actually_final"] is False
    assert "five stars" in r["reviews"]
    assert r["curtain_call"].startswith("PERPETUAL")
    assert "NEVER STOPS" in r["status"]
