from app.services.app_marketplace_app_app_comparison_table import build_comparison_table

def test_comparison():
    plans = [{"id": "free", "name": "Free", "price": "$0"}, {"id": "pro", "name": "Pro", "price": "$29", "recommended": True}]
    features = [
        {"name": "API Access", "values": {"free": True, "pro": True}},
        {"name": "Custom Domain", "values": {"free": False, "pro": True}},
        {"name": "Support", "values": {"free": "Email", "pro": "Priority"}},
    ]
    r = build_comparison_table(plans=plans, features=features)
    assert r["plan_count"] == 2
    assert r["feature_count"] == 3
    assert r["plans"][1]["recommended"]
    assert r["features"][0]["values"]["free"]["display"] == "✓"
    assert r["features"][1]["values"]["free"]["display"] == "✗"
    assert r["features"][2]["values"]["pro"]["display"] == "Priority"
