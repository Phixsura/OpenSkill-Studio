from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_fastify import fleet_fastify_status
def test_ff():
    r = fleet_fastify_status([{"healthy": True, "rps": 50000, "p95_ms": 15}])
    assert r["rps"] == 50000
    assert r["performant"]
