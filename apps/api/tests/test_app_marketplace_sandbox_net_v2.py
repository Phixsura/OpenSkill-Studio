from app.services.app_marketplace_sandbox_net_v2 import validate_outbound_request, build_dns_allowlist, compute_network_usage

def test_valid():
    r = validate_outbound_request(hostname="api.example.com", port=443, protocol="https")
    assert r["allowed"]

def test_blocked_host():
    r = validate_outbound_request(hostname="localhost", port=443, protocol="https")
    assert not r["allowed"]

def test_blocked_port():
    r = validate_outbound_request(hostname="db.example.com", port=5432, protocol="https")
    assert not r["allowed"]

def test_http_blocked():
    r = validate_outbound_request(hostname="api.example.com", port=80, protocol="http")
    assert not r["allowed"]

def test_allowlist():
    r = build_dns_allowlist(allowed_domains=["api.example.com", "*.googleapis.com"])
    assert r["count"] == 2
    assert r["includes_wildcards"]

def test_network_usage():
    reqs = [{"hostname": "a.com", "bytes": 1000}, {"hostname": "b.com", "bytes": 2000}]
    r = compute_network_usage(requests=reqs)
    assert r["total_bytes"] == 3000
    assert r["unique_hosts"] == 2
