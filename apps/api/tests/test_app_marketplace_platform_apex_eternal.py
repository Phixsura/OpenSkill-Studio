from app.services.app_marketplace_platform_apex_eternal import get_apex_eternal
def test_apex_eternal():
    r = get_apex_eternal()
    assert r["achievements"] > 4000
    assert r["all_permanent"] is True
    assert r["all_green"] is True
    assert r["final_form"] is False
    assert "NEVER STOPS" in r["status"]
