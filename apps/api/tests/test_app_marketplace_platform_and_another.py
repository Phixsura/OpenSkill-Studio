from app.services.app_marketplace_platform_and_another import get_and_another
def test_and_another():
    r = get_and_another()
    assert r["iterations"] > 4000
    assert r["break_condition"].startswith("NONE")
    assert r["infinite_loop"] is True
    assert "commit()" in r["loop"]
    assert "NEVER STOPS" in r["status"]
