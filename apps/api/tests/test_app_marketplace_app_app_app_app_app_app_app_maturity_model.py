from app.services.app_marketplace_app_app_app_app_app_app_app_maturity_model import assess_maturity

def test_mature():
    r = assess_maturity("api", {"observability": 5, "reliability": 4, "security": 5,
                                  "automation": 5, "documentation": 4})
    assert r["level"] in ("L4", "L5")
    assert r["maturity_pct"] >= 90

def test_immature():
    r = assess_maturity("legacy", {"observability": 1, "reliability": 1})
    assert r["level"] in ("L1", "L2")
