from app.services.app_marketplace_app_app_plan_comparison import compare_plans

def test_all():
    r = compare_plans()
    assert r["total_plans"] == 4
    assert r["total_features"] >= 5
    free = next(p for p in r["plans"] if p["id"] == "free")
    assert free["price_label"] == "Free"
    pro = next(p for p in r["plans"] if p["id"] == "pro")
    assert pro["apps_label"] == "Unlimited"

def test_subset():
    r = compare_plans(plan_ids=["free", "pro"])
    assert r["total_plans"] == 2
