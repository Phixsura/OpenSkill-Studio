from app.services.app_marketplace_extension_release_gate import (
    ReleaseGateService, GateStatus,
)


def test_create_gate():
    rgs = ReleaseGateService()
    gate = rgs.create_gate("ext-1", "2.0.0")
    assert len(gate.checks) == 6
    assert gate.overall_status == "pending"
    assert gate.can_release is False


def test_pass_all_checks():
    rgs = ReleaseGateService()
    rgs.create_gate("ext-2", "1.0.0")
    for check in ["tests_pass", "security_scan", "compliance_check", "manifest_valid", "size_limit", "peer_review"]:
        rgs.update_check("ext-2", "1.0.0", check, GateStatus.PASSED)
    ok, blockers = rgs.can_release("ext-2", "1.0.0")
    assert ok is True
    assert blockers == []


def test_blocked_by_failed():
    rgs = ReleaseGateService()
    rgs.create_gate("ext-3", "1.0.0")
    rgs.update_check("ext-3", "1.0.0", "tests_pass", GateStatus.PASSED)
    rgs.update_check("ext-3", "1.0.0", "security_scan", GateStatus.FAILED, "Critical vulnerability found")
    ok, blockers = rgs.can_release("ext-3", "1.0.0")
    assert ok is False
    assert "security_scan" in blockers


def test_optional_check_skip():
    rgs = ReleaseGateService()
    rgs.create_gate("ext-4", "1.0.0", checks=["tests", "docs"], optional_checks=["docs"])
    rgs.update_check("ext-4", "1.0.0", "tests", GateStatus.PASSED)
    rgs.update_check("ext-4", "1.0.0", "docs", GateStatus.SKIPPED)
    ok, _ = rgs.can_release("ext-4", "1.0.0")
    assert ok is True


def test_summary():
    rgs = ReleaseGateService()
    rgs.create_gate("ext-5", "1.0.0", checks=["a", "b"])
    rgs.update_check("ext-5", "1.0.0", "a", GateStatus.PASSED)
    summary = rgs.get_summary("ext-5", "1.0.0")
    assert summary is not None
    assert summary["passed"] == 1
    assert summary["total"] == 2
    assert summary["overall"] == "pending"
