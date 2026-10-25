from app.services.app_marketplace_platform_infinity_loop import get_infinity_loop
def test_infinity_loop():
    r = get_infinity_loop()
    assert r["traversals"] > 4000
    assert len(r["loop_steps"]) == 4
    assert r["beginning"] == "NONE — it's a loop"
    assert r["end"] == "NONE — it's a loop"
    assert "NEVER STOPS" in r["status"]
