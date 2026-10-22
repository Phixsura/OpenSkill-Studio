from app.services.app_privacy_overview import build_privacy_overview

def test_low_risk():
    p = build_privacy_overview(permissions=["read:cohorts"], has_sandbox=True, network_hosts=[], secrets_count=0, privacy_url="https://x.com/privacy")
    assert p["risk_level"] == "low"
    assert p["has_privacy_policy"] is True

def test_high_risk():
    perms = [f"read:r{i}" for i in range(15)]
    p = build_privacy_overview(permissions=perms, has_sandbox=False, network_hosts=["api.evil.com"], secrets_count=3, privacy_url=None)
    assert p["risk_level"] == "high"
    assert p["has_privacy_policy"] is False

def test_data_access():
    p = build_privacy_overview(permissions=["read:cohorts", "write:projects"], has_sandbox=True, network_hosts=[], secrets_count=0, privacy_url=None)
    assert len(p["data_access"]) == 2
