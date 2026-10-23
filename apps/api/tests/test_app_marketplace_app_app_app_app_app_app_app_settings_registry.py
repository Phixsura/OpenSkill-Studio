from app.services.app_marketplace_app_app_app_app_app_app_app_settings_registry import get_defaults, validate_settings, merge_settings

def test_defaults():
    d = get_defaults()
    assert d["general"]["platform_name"] == "OpenSkill"
    assert d["security"]["mfa_required"] is False

def test_validate():
    r = validate_settings({"security": {"session_timeout_min": 3}})
    assert not r["valid"]
    r2 = validate_settings({"security": {"session_timeout_min": 60}})
    assert r2["valid"]

def test_merge():
    d = get_defaults()
    m = merge_settings(d, {"general": {"platform_name": "MyPlatform"}, "security": {"mfa_required": True}})
    assert m["general"]["platform_name"] == "MyPlatform"
    assert m["security"]["mfa_required"] is True
    assert m["general"]["support_email"] == "support@openskill.io"  # kept default
