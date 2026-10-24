from app.services.app_marketplace_app_app_app_app_app_app_app_dns_health import check_dns, propagation_status

def test_check():
    r = check_dns("app.example.com", [
        {"type": "A", "value": "1.2.3.4", "ttl": 300},
        {"type": "CNAME", "value": "proxy.example.com"},
        {"type": "TXT", "value": ""},
    ])
    assert r["resolved"] == 2
    assert not r["all_ok"]

def test_propagation():
    r = propagation_status([
        {"region": "us-east", "propagated": True},
        {"region": "eu-west", "propagated": True},
        {"region": "ap-south", "propagated": False},
    ])
    assert r["propagated"] == 2
    assert r["progress_pct"] == 67
    assert not r["complete"]
