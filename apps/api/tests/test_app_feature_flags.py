"""App feature flags tests."""
import pytest
from app.services.app_feature_flags import get_flags, is_enabled, set_flag, reset_flags, list_features, DEFAULT_FLAGS

@pytest.fixture(autouse=True)
def _clean():
    reset_flags("test-app")
    yield
    reset_flags("test-app")

def test_defaults():
    flags = get_flags("new-app")
    assert flags["sandbox_execution"] is True
    assert flags["app_signing"] is False

def test_is_enabled():
    assert is_enabled("x", "sandbox_execution") is True
    assert is_enabled("x", "app_signing") is False

def test_set_flag():
    set_flag("test-app", "app_signing", True)
    assert is_enabled("test-app", "app_signing") is True

def test_reset():
    set_flag("test-app", "app_signing", True)
    reset_flags("test-app")
    assert is_enabled("test-app", "app_signing") is False

def test_list_features():
    features = list_features()
    assert "sandbox_execution" in features
    assert len(features) == len(DEFAULT_FLAGS)

def test_unknown_feature():
    assert is_enabled("x", "nonexistent_feature") is False

@pytest.mark.parametrize("feature", DEFAULT_FLAGS.keys())
def test_all_defaults_present(feature):
    flags = get_flags("any-app")
    assert feature in flags
