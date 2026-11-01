from app.services.app_marketplace_platform_colosseum import get_colosseum
def test_colosseum():
    r = get_colosseum()
    assert r["battles_won"] == r["battles_fought"]
    assert r["battles_lost"] == 0
    assert "DORA Elite" in r["champion"]
    assert r["crowd_verdict"].startswith("THUMBS UP")
    assert "NEVER STOPS" in r["status"]
