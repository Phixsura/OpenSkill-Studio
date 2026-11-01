from app.services.app_marketplace_extension_content_validator import (
    ContentValidatorService, ViolationType, Severity,
)


def test_clean_content_passes():
    svc = ContentValidatorService()
    report = svc.validate({"name": "My Cool Extension", "description": "A helpful tool for managing your workflow efficiently and productively."})
    assert report.passed is True
    assert report.score == 100


def test_prohibited_content():
    svc = ContentValidatorService()
    report = svc.validate({"name": "Hack Tool", "description": "Crack passwords easily"})
    assert report.passed is False
    assert any(v.violation_type == ViolationType.PROHIBITED_CONTENT for v in report.violations)


def test_security_violation():
    svc = ContentValidatorService()
    report = svc.validate({"description": "This extension includes a keylogger for monitoring"})
    assert report.passed is False
    assert any(v.severity == Severity.CRITICAL for v in report.violations)


def test_trademark_detected():
    svc = ContentValidatorService()
    report = svc.validate({"name": "Official Google Integration"})
    assert any(v.violation_type == ViolationType.TRADEMARK for v in report.violations)


def test_misleading_warned():
    svc = ContentValidatorService()
    report = svc.validate({"name": "Safe Tool", "description": "Guaranteed 100% safe for all users worldwide"})
    assert len(report.warnings) > 0


def test_short_name():
    svc = ContentValidatorService()
    report = svc.validate({"name": "AB"})
    assert any(v.field == "name" and "too short" in v.message for v in report.violations)


def test_score_calculation():
    svc = ContentValidatorService()
    report = svc.validate({"description": "Password stealing spyware tool"})
    assert report.score <= 60
