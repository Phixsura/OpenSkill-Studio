from app.services.app_marketplace_app_install_wizard_v2 import build_install_wizard, validate_install_config

def test_wizard():
    w = build_install_wizard(app={"name": "App"}, required_scopes=["read"], optional_scopes=["write"],
                               config_fields=[{"name": "url", "type": "string"}])
    assert w["step_count"] == 3
    assert w["has_config"]

def test_validate_ok():
    r = validate_install_config(config={"url": "https://x.com"}, required_fields=["url"])
    assert r["valid"]

def test_validate_missing():
    r = validate_install_config(config={}, required_fields=["url", "key"])
    assert not r["valid"]
    assert len(r["missing_fields"]) == 2
