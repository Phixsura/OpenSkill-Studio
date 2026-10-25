from app.services.app_marketplace_platform_chronicle import get_chronicle
def test_chronicle():
    r = get_chronicle()
    assert r["chapters"] > 4000
    assert r["entries"] > 900000
    assert len(r["notable_events"]) == 4
    assert r["final_chapter"].startswith("UNWRITTEN")
    assert "NEVER STOPS" in r["status"]
