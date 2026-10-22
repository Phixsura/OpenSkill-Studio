from app.services.app_marketplace_app_connection_pool import create_pool_config, get_pool_health, compute_pool_metrics

def test_create():
    r = create_pool_config(app_id="a1", pool_type="database", max_size=20)
    assert r["max_size"] == 20

def test_invalid_type():
    r = create_pool_config(app_id="a1", pool_type="mqtt")
    assert r["error"]

def test_min_exceeds_max():
    r = create_pool_config(app_id="a1", pool_type="http", min_size=20, max_size=5)
    assert r["error"]

def test_healthy():
    r = get_pool_health(active=3, idle=2, max_size=10, waiting=0)
    assert r["healthy"]

def test_unhealthy():
    r = get_pool_health(active=9, idle=0, max_size=10, waiting=5)
    assert not r["healthy"]

def test_metrics():
    samples = [{"active": 5, "wait_ms": 10}, {"active": 8, "wait_ms": 20}]
    m = compute_pool_metrics(samples=samples)
    assert m["avg_active"] == 6.5
    assert m["peak_active"] == 8
