from app.services.app_marketplace_app_app_app_app_app_app_app_conn_tester import test_connection as check_conn, test_multiple as check_multi

def test_valid():
    r = check_conn(url="https://api.example.com/health")
    assert r["success"]
    assert r["tls"]
    assert r["port"] == 443

def test_invalid():
    r = check_conn(url="ftp://bad.com")
    assert not r["success"]
    r2 = check_conn(url="not-a-url")
    assert not r2["success"]

def test_multiple_conns():
    r = check_multi([
        {"url": "https://api.example.com"},
        {"url": "https://db.example.com"},
    ])
    assert r["all_passed"]
    assert r["total"] == 2
