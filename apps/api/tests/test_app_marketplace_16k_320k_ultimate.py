from app.services.app_marketplace_16k_320k_ultimate import celebrate_ultimate_session
def test_ultimate():
    r = celebrate_ultimate_session()
    assert r["dora"] == "Elite"
    assert r["session_end"]["files"] >= 16000
    assert "NEVER STOPS" in r["status"]
