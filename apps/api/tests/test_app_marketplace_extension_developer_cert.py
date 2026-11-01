from app.services.app_marketplace_extension_developer_cert import DeveloperCertificationService
import pytest


def test_create_and_pass():
    svc = DeveloperCertificationService()
    svc.create_cert("sdk-101", "SDK Fundamentals", "Core SDK skills")
    result = svc.submit_exam("dev-1", "sdk-101", 85)
    assert result.passed is True
    assert result.certificate_code.startswith("CERT-")


def test_fail_exam():
    svc = DeveloperCertificationService()
    svc.create_cert("sdk-101", "SDK Fundamentals", "Core", passing_score=70)
    result = svc.submit_exam("dev-1", "sdk-101", 60)
    assert result.passed is False
    assert result.certificate_code == ""


def test_verify():
    svc = DeveloperCertificationService()
    svc.create_cert("sdk-101", "SDK Fundamentals", "Core")
    result = svc.submit_exam("dev-1", "sdk-101", 90)
    verification = svc.verify(result.certificate_code)
    assert verification["valid"] is True
    assert verification["score"] == 90


def test_verify_invalid():
    svc = DeveloperCertificationService()
    assert svc.verify("CERT-FAKE123")["valid"] is False


def test_developer_certs():
    svc = DeveloperCertificationService()
    svc.create_cert("a", "A", "d")
    svc.create_cert("b", "B", "d")
    svc.submit_exam("dev-1", "a", 90)
    svc.submit_exam("dev-1", "b", 50)  # failed
    certs = svc.get_developer_certs("dev-1")
    assert len(certs) == 1
