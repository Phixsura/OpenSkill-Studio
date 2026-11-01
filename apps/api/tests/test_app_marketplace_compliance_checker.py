from app.services.app_marketplace_compliance_checker import ComplianceChecker


VALID_META = {"name": "my-ext", "version": "1.0.0", "description": "A tool",
              "author": "alice", "license": "MIT"}


def test_fully_compliant():
    cc = ComplianceChecker()
    result = cc.run_all(VALID_META, size_bytes=1024)
    assert result["compliant"] is True
    assert len(result["errors"]) == 0


def test_missing_license():
    cc = ComplianceChecker()
    r = cc.check_license("")
    assert r.passed is False


def test_unapproved_license():
    cc = ComplianceChecker()
    r = cc.check_license("WTFPL")
    assert r.passed is False
    assert r.severity == "warning"


def test_missing_metadata():
    cc = ComplianceChecker()
    result = cc.run_all({"name": "test-ext"})
    assert result["compliant"] is False
    assert any("version" in e["message"] for e in result["errors"])


def test_prohibited_name():
    cc = ComplianceChecker()
    meta = {**VALID_META, "name": "test"}
    result = cc.run_all(meta)
    assert result["compliant"] is False
    assert any("prohibited" in e["message"] for e in result["errors"])


def test_size_limit():
    cc = ComplianceChecker()
    r = cc.check_size(100 * 1024 * 1024)  # 100MB
    assert r.passed is False


def test_too_many_deps():
    cc = ComplianceChecker()
    r = cc.check_dependencies([f"dep-{i}" for i in range(150)])
    assert r.passed is False
