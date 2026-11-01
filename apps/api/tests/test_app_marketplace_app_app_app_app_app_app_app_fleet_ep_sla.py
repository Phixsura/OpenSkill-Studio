from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ep_sla import fleet_endpoint_sla
def test_sla():
    r = fleet_endpoint_sla([{"p99_ms": 200, "sla_ms": 500}, {"p99_ms": 600, "sla_ms": 500}])
    assert r["meeting_sla"] == 1
    assert r["violating"] == 1
    assert r["compliance_pct"] == 50.0
