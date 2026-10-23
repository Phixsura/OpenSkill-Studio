from app.services.app_marketplace_app_app_launch_checklist import evaluate_launch_readiness

def test_partial():
    r = evaluate_launch_readiness(completed=["branding", "description", "pricing"])
    assert r["completed"] == 3
    assert r["readiness_pct"] == 30
    assert not r["launch_ready"]

def test_full():
    all_ids = [i["id"] for i in __import__("app.services.app_marketplace_app_app_launch_checklist",
        fromlist=["LAUNCH_ITEMS"]).LAUNCH_ITEMS]
    r = evaluate_launch_readiness(completed=all_ids)
    assert r["launch_ready"]
    assert r["readiness_pct"] == 100

def test_categories():
    r = evaluate_launch_readiness(completed=["testing", "security", "performance"])
    eng = next(c for c in r["categories"] if c["category"] == "engineering")
    assert eng["done"] == 3
    assert eng["pct"] == 100
