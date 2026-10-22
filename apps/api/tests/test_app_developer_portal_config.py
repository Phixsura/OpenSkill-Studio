from app.services.app_developer_portal_config import get_portal_config, is_feature_enabled

def test_config():
    c = get_portal_config()
    assert "features" in c
    assert "limits" in c
    assert "links" in c

def test_feature_enabled():
    assert is_feature_enabled("app_creation") is True

def test_feature_disabled():
    assert is_feature_enabled("billing") is False

def test_unknown_feature():
    assert is_feature_enabled("nonexistent") is False
