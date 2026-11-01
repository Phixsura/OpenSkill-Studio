from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ip_allowlist_v9 import fleet_ip_allowlist_v9
def test_ip_v9():
    r = fleet_ip_allowlist_v9([{"active": True, "blocked_today": 50, "cidr": "10.0.0.0/8"}])
    assert r["unique_cidrs"] == 1
    assert r["healthy"]
