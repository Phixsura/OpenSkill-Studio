from app.services.app_marketplace_app_app_ip_geolocation import lookup_ip, build_geo_distribution

def test_lookup():
    r = lookup_ip(ip="1.2.3.4")
    assert r["country"] == "AU"
    assert r["city"] == "Sydney"
    assert not r["is_private"]

def test_private():
    r = lookup_ip(ip="10.0.0.1")
    assert r["is_private"]

def test_distribution():
    ips = ["1.1.1.1", "1.2.3.4", "8.8.8.8"]
    r = build_geo_distribution(ips=ips)
    assert r["countries"] == 2
    assert r["total_ips"] == 3
