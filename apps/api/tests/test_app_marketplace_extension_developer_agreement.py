from app.services.app_marketplace_extension_developer_agreement import (
    DeveloperAgreementService, ComplianceStatus,
)
import pytest


def test_publish_and_accept():
    svc = DeveloperAgreementService()
    svc.publish_version("1.0", "Developer ToS", "hash123")
    acc = svc.accept("dev-1")
    assert acc.agreement_version == "1.0"
    assert svc.has_accepted_current("dev-1") is True


def test_not_accepted():
    svc = DeveloperAgreementService()
    svc.publish_version("1.0", "ToS", "h1")
    assert svc.has_accepted_current("dev-1") is False


def test_re_acceptance_required():
    svc = DeveloperAgreementService()
    svc.publish_version("1.0", "ToS", "h1")
    svc.accept("dev-1")
    svc.publish_version("2.0", "Updated ToS", "h2", requires_re_acceptance=True)
    assert svc.needs_re_acceptance("dev-1") is True
    svc.accept("dev-1", "2.0")
    assert svc.needs_re_acceptance("dev-1") is False


def test_violation_escalation():
    svc = DeveloperAgreementService()
    svc.record_violation("dev-1", "Malware distribution")
    c = svc.get_compliance("dev-1")
    assert c["status"] == "violation"
    svc.record_violation("dev-1", "Data harvesting")
    svc.record_violation("dev-1", "Spam reviews")
    c2 = svc.get_compliance("dev-1")
    assert c2["is_suspended"] is True


def test_warning():
    svc = DeveloperAgreementService()
    svc.issue_warning("dev-1")
    c = svc.get_compliance("dev-1")
    assert c["status"] == "warning"
    assert c["warnings"] == 1


def test_invalid_version():
    svc = DeveloperAgreementService()
    with pytest.raises(ValueError, match="not found"):
        svc.accept("dev-1", "99.0")


def test_clean_developer():
    svc = DeveloperAgreementService()
    c = svc.get_compliance("new-dev")
    assert c["status"] == "compliant"
    assert c["violations"] == 0
