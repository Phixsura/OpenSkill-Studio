from app.services.app_marketplace_app_app_app_app_app_app_app_conn_tester import test_connection, test_multiple

def test_valid():
    r = test_connection(url="https://api.example.com/health")
    assert r["success"]
    assert r["tls"]
    assert r["port"] == 443

def test_invalid():
    r = test_connection(url="ftp://bad.com")
    assert not r["success"]
    r2 = test_connection(url="not-a-url")
    assert not r2["success"]

def test_multiple_conns():
    r = test_multiple([
        {"url": "https://api.example.com"},
        {"url": "https://db.example.com"},
    ])
    assert r["all_passed"]
    assert r["total"] == 2
