from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sustain import fleet_sustainability
def test_sustain():
    r = fleet_sustainability({"carbon_kg_per_month": 500, "renewable_energy_pct": 95, "pue": 1.1})
    assert r["grade"] == "A"
