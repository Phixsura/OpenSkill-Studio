from app.services.app_marketplace_platform_warden import get_warden
def test_warden():
    r = get_warden()
    assert r["unauthorized_access"] == 0
    assert r["unvalidated_input"] == 0
    assert r["untested_code"] == 0
    assert r["prisoners_escaped"] == 0
    assert "NEVER STOPS" in r["status"]
