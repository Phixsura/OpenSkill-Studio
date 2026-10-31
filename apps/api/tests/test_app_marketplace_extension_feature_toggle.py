from app.services.app_marketplace_extension_feature_toggle import (
    FeatureToggleService, ToggleType,
)
import pytest


def test_boolean_toggle():
    svc = FeatureToggleService()
    svc.create("ext-1", "dark_mode", ToggleType.BOOLEAN)
    assert svc.is_enabled("ext-1", "dark_mode") is False
    svc.enable("ext-1", "dark_mode")
    assert svc.is_enabled("ext-1", "dark_mode") is True


def test_user_list_toggle():
    svc = FeatureToggleService()
    svc.create("ext-1", "beta_feature", ToggleType.USER_LIST)
    svc.enable("ext-1", "beta_feature")
    svc.add_users("ext-1", "beta_feature", ["user-1", "user-2"])
    assert svc.is_enabled("ext-1", "beta_feature", "user-1") is True
    assert svc.is_enabled("ext-1", "beta_feature", "user-3") is False


def test_percentage_rollout():
    svc = FeatureToggleService()
    svc.create("ext-1", "new_ui", ToggleType.PERCENTAGE, percentage=50)
    svc.enable("ext-1", "new_ui")
    # With 100 users, ~50% should get it (deterministic hash)
    enabled_count = sum(1 for i in range(100)
                        if svc.is_enabled("ext-1", "new_ui", f"user-{i}"))
    assert 30 <= enabled_count <= 70  # roughly 50%


def test_percentage_deterministic():
    svc = FeatureToggleService()
    svc.create("ext-1", "flag", ToggleType.PERCENTAGE, percentage=50)
    svc.enable("ext-1", "flag")
    r1 = svc.is_enabled("ext-1", "flag", "user-42")
    r2 = svc.is_enabled("ext-1", "flag", "user-42")
    assert r1 == r2  # same user always gets same result


def test_disable():
    svc = FeatureToggleService()
    svc.create("ext-1", "f", ToggleType.BOOLEAN)
    svc.enable("ext-1", "f")
    svc.disable("ext-1", "f")
    assert svc.is_enabled("ext-1", "f") is False


def test_get_all_flags():
    svc = FeatureToggleService()
    svc.create("ext-1", "a", ToggleType.BOOLEAN)
    svc.create("ext-1", "b", ToggleType.BOOLEAN)
    svc.enable("ext-1", "a")
    flags = svc.get_all_flags("ext-1", "user-1")
    assert flags == {"a": True, "b": False}


def test_invalid_percentage():
    svc = FeatureToggleService()
    with pytest.raises(ValueError):
        svc.create("ext-1", "f", ToggleType.PERCENTAGE, percentage=150)


def test_remove_user():
    svc = FeatureToggleService()
    svc.create("ext-1", "beta", ToggleType.USER_LIST)
    svc.enable("ext-1", "beta")
    svc.add_users("ext-1", "beta", ["u1"])
    assert svc.is_enabled("ext-1", "beta", "u1") is True
    svc.remove_user("ext-1", "beta", "u1")
    assert svc.is_enabled("ext-1", "beta", "u1") is False
