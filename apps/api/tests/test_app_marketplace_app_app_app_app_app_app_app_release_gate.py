from app.services.app_marketplace_app_app_app_app_app_app_app_release_gate import ReleaseGateController

def test_gates():
    rgc = ReleaseGateController()
    rgc.define_release("v2.0", [
        {"name": "tests", "required": True},
        {"name": "security_scan", "required": True},
        {"name": "perf_test", "required": False},
    ])
    rgc.pass_gate("v2.0", "tests")
    r = rgc.can_release("v2.0")
    assert not r["can_release"]
    assert "security_scan" in r["pending_gates"]
    rgc.pass_gate("v2.0", "security_scan")
    r2 = rgc.can_release("v2.0")
    assert r2["can_release"]  # perf_test optional
