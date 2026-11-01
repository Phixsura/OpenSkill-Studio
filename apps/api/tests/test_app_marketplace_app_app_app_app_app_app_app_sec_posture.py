from app.services.app_marketplace_app_app_app_app_app_app_app_sec_posture import assess_posture

def test_strong():
    r = assess_posture(["mfa_enabled", "encryption_at_rest", "encryption_in_transit",
                          "vulnerability_scanning", "dependency_auditing", "audit_logging",
                          "incident_response_plan", "secrets_rotation", "network_segmentation"])
    assert r["score"] == 100
    assert r["grade"] == "A"

def test_weak():
    r = assess_posture(["mfa_enabled", "audit_logging"])
    assert r["grade"] in ("C", "D")
    assert r["implemented"] == 2
