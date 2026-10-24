from app.services.app_marketplace_app_app_app_app_app_app_app_dns_health import check_dns_health, detect_stale_records

def test_health():
    r = check_dns_health([
        {"domain": "api.example.com", "resolved": True, "ttl": 300, "ip": "1.2.3.4"},
        {"domain": "bad.example.com", "resolved": False, "ttl": 0},
    ])
    assert r["healthy"] == 1
    assert r["unhealthy"] == 1
    assert not r["all_healthy"]

def test_stale():
    r = detect_stale_records([
        {"domain": "a.com", "ttl": 100000},
        {"domain": "b.com", "ttl": 3600},
    ], max_ttl=86400)
    assert len(r) == 1
    assert r[0]["domain"] == "a.com"
