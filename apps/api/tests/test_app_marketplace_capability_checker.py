from app.services.app_marketplace_capability_checker import CapabilityChecker


def test_all_available():
    cc = CapabilityChecker()
    ok, results = cc.check(["filesystem", "crypto", "timers"])
    assert ok is True
    assert all(r["ok"] for r in results)


def test_unavailable_capability():
    cc = CapabilityChecker()
    ok, results = cc.check(["filesystem", "subprocess"])
    assert ok is False
    failed = [r for r in results if not r["ok"]]
    assert len(failed) == 1
    assert failed[0]["capability"] == "subprocess"


def test_restricted_capability():
    cc = CapabilityChecker()
    ok, results = cc.check(["network.outbound"])
    assert ok is True
    assert results[0]["status"] == "restricted"
    assert "allowlist-only" in results[0]["restrictions"]


def test_deprecated_capability():
    cc = CapabilityChecker()
    ok, results = cc.check(["gpu"])
    assert ok is True
    assert results[0]["status"] == "deprecated"


def test_unknown_capability():
    cc = CapabilityChecker()
    ok, results = cc.check(["quantum_compute"])
    assert ok is False
    assert results[0]["status"] == "unknown"


def test_list_available():
    cc = CapabilityChecker()
    available = cc.list_available()
    assert "filesystem" in available
    assert "crypto" in available
    assert "subprocess" not in available


def test_is_available():
    cc = CapabilityChecker()
    assert cc.is_available("filesystem") is True
    assert cc.is_available("network.outbound") is True  # restricted = available
    assert cc.is_available("subprocess") is False
    assert cc.is_available("nonexistent") is False
