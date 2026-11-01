from app.services.app_marketplace_app_app_app_app_app_app_app_tls_terminator import TlsTerminator

def test_terminate():
    tls = TlsTerminator()
    tls.add_cert("api.example.com", "sha256:abc", 90)
    r = tls.terminate("api.example.com")
    assert r["terminated"]
    assert r["protocol"] == "TLS 1.3"

def test_no_cert():
    tls = TlsTerminator()
    r = tls.terminate("unknown.com")
    assert not r["terminated"]

def test_expired():
    tls = TlsTerminator()
    tls.add_cert("old.com", "sha256:old", 0)
    r = tls.terminate("old.com")
    assert not r["terminated"]
    assert r["reason"] == "cert_expired"

def test_stats():
    tls = TlsTerminator()
    tls.add_cert("a.com", "h1", 90)
    tls.add_cert("b.com", "h2", 15)
    s = tls.stats()
    assert s["expiring_soon"] == 1
