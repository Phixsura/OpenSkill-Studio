from app.services.app_marketplace_app_app_app_app_app_app_app_usage_billing import calculate_tiered_cost, project_monthly

def test_tiered():
    r = calculate_tiered_cost(5000)
    assert r["usage"] == 5000
    assert len(r["breakdown"]) == 2  # free tier + second tier
    assert r["breakdown"][0]["cost"] == 0  # first 1000 free
    assert r["breakdown"][1]["units"] == 4000
    assert r["total_cost"] == 20.0  # 4000 * 0.005

def test_project():
    r = project_monthly(500)
    assert r["projected_monthly"] == 15000
    assert r["projected_cost"] > 0
