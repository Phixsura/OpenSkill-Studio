from app.services.app_marketplace_feature_flags import FeatureFlagService


def test_create_and_default_disabled():
    ffs = FeatureFlagService()
    ffs.create_flag("f1", "ext-1", "Dark Mode")
    assert ffs.is_enabled("f1") is False


def test_global_toggle():
    ffs = FeatureFlagService()
    ffs.create_flag("f2", "ext-1", "New UI")
    ffs.enable_globally("f2")
    assert ffs.is_enabled("f2", org_id="any") is True
    ffs.disable_globally("f2")
    assert ffs.is_enabled("f2") is False


def test_org_enable():
    ffs = FeatureFlagService()
    ffs.create_flag("f3", "ext-1", "Beta Feature")
    ffs.enable_for_org("f3", "org-1")
    assert ffs.is_enabled("f3", org_id="org-1") is True
    assert ffs.is_enabled("f3", org_id="org-2") is False


def test_org_disable_overrides_global():
    ffs = FeatureFlagService()
    ffs.create_flag("f4", "ext-1", "Risky Feature")
    ffs.enable_globally("f4")
    ffs.disable_for_org("f4", "org-blocked")
    assert ffs.is_enabled("f4", org_id="org-blocked") is False
    assert ffs.is_enabled("f4", org_id="org-ok") is True


def test_percentage_rollout():
    ffs = FeatureFlagService()
    ffs.create_flag("f5", "ext-1", "Gradual Rollout")
    ffs.set_rollout("f5", 50)
    # Test multiple users, some should be enabled, some not (deterministic)
    results = [ffs.is_enabled("f5", user_id=f"user-{i}") for i in range(100)]
    enabled_count = sum(results)
    # With 50% rollout, expect roughly 40-60 out of 100
    assert 20 < enabled_count < 80


def test_user_explicit_enable():
    ffs = FeatureFlagService()
    ffs.create_flag("f6", "ext-1", "VIP Feature")
    flag = ffs.get_flag("f6")
    flag.enabled_users.add("vip-user")
    assert ffs.is_enabled("f6", user_id="vip-user") is True
    assert ffs.is_enabled("f6", user_id="normal-user") is False


def test_list_flags():
    ffs = FeatureFlagService()
    ffs.create_flag("fa", "ext-a", "A")
    ffs.create_flag("fb", "ext-b", "B")
    ffs.create_flag("fc", "ext-a", "C")
    assert len(ffs.list_flags()) == 3
    assert len(ffs.list_flags("ext-a")) == 2
