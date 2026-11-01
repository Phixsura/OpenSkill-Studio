from app.services.app_marketplace_platform_final_frontier import get_final_frontier
def test_final_frontier():
    r = get_final_frontier()
    assert r["frontiers_crossed"] > 4000
    assert r["final"] is False
    assert "boldly" in r["mission"]
    assert r["warp_status"].startswith("ENGAGED")
    assert "NEVER STOPS" in r["status"]
