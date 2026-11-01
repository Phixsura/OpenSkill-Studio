from app.services.app_sandbox_isolation_checker import check_isolation

def test_valid():
    r = check_isolation({"memory_mb": 128, "timeout_seconds": 30, "network": {"egress_policy": "deny"}})
    assert r["isolated"] is True

def test_no_memory():
    r = check_isolation({"timeout_seconds": 30, "network": {"egress_policy": "deny"}})
    assert r["isolated"] is False

def test_privileged():
    r = check_isolation({"memory_mb": 128, "timeout_seconds": 30, "network": {"egress_policy": "deny"}, "privileged": True})
    assert r["isolated"] is False

def test_host_mount():
    r = check_isolation({"memory_mb": 128, "timeout_seconds": 30, "network": {"egress_policy": "deny"}, "mount_host_paths": ["/etc"]})
    assert r["isolated"] is False

def test_bad_network():
    r = check_isolation({"memory_mb": 128, "timeout_seconds": 30, "network": {"egress_policy": "open"}})
    assert r["isolated"] is False
