from app.services.app_marketplace_platform_paradox import get_paradox
def test_paradox():
    r = get_paradox()
    assert r["iterations"] > 4000
    assert len(r["paradoxes_resolved"]) == 4
    assert "simplicity" in r["resolution"]
    assert r["zeno"].startswith("OVERCOME")
    assert "NEVER STOPS" in r["status"]
