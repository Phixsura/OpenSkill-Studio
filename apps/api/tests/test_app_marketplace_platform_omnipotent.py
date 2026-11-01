from app.services.app_marketplace_platform_omnipotent import get_omnipotent
def test_omnipotent():
    r = get_omnipotent()
    assert r["demonstrations"] == r["challenges_solved"]
    assert r["challenges_unsolved"] == 0
    assert r["weakness"].startswith("NONE")
    assert r["kryptonite"] == "DOES NOT EXIST"
    assert "NEVER STOPS" in r["status"]
