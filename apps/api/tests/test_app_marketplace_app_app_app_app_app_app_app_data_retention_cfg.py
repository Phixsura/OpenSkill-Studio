from app.services.app_marketplace_app_app_app_app_app_app_app_data_retention_cfg import get_retention_preset, validate_retention, list_presets

def test_preset():
    r = get_retention_preset("compliance")
    assert r["config"]["logs"] == 365
    assert r["display"]["logs"] == "365 days"

def test_validate():
    assert validate_retention({"logs": 30, "user_data": 90})["valid"]
    assert not validate_retention({"user_data": 10})["valid"]

def test_presets():
    assert len(list_presets()) == 4
