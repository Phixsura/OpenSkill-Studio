from app.services.app_marketplace_app_app_app_app_app_app_app_sre_toolkit import (
    calculate_error_budget_burn, toil_budget,
)

def test_burn():
    r = calculate_error_budget_burn(99.9, 30, 15, 500, 1000000)
    assert r["budget_total"] == 1000
    assert r["consumed_pct"] == 50.0
    assert r["burn_rate"] == 1.0
    assert r["healthy"]

def test_burn_alert():
    r = calculate_error_budget_burn(99.9, 30, 3, 800, 1000000)
    assert r["burn_rate"] > 5
    assert r["alert"] in ("page", "ticket")

def test_toil():
    r = toil_budget(160, 60)
    assert r["toil_pct"] == 37.5
    assert r["within_budget"]
