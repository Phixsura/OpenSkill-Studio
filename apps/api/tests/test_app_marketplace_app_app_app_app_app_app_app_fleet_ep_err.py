from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ep_err import fleet_endpoint_errors
def test_ep_err():
    r = fleet_endpoint_errors([{"name": "/api/users", "error_rate_pct": 1}, {"name": "/api/orders", "error_rate_pct": 12}])
    assert r["noisy_endpoints"] == 1
    assert r["worst"] == "/api/orders"
    assert r["worst_rate"] == 12
