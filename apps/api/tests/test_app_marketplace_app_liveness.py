from app.services.app_marketplace_app_liveness import liveness_check
def test_alive():
    r = liveness_check()
    assert r["alive"]
    assert r["pid"] > 0
