from app.services.app_marketplace_extension_feature_flag_svc import ExtFeatureFlagSvcService

def test_create_and_enable():
    svc = ExtFeatureFlagSvcService()
    svc.create("ext-1", "dark-mode", "Dark Mode")
    assert svc.is_enabled("ext-1", "dark-mode") is False
    svc.set_enabled("ext-1", "dark-mode", True)
    assert svc.is_enabled("ext-1", "dark-mode") is False  # no rollout, no allowlist

def test_rollout():
    svc = ExtFeatureFlagSvcService()
    svc.create("ext-1", "new-ui", "New UI")
    svc.set_rollout("ext-1", "new-ui", 100)
    assert svc.is_enabled("ext-1", "new-ui", "any-user") is True

def test_allowlist():
    svc = ExtFeatureFlagSvcService()
    svc.create("ext-1", "beta", "Beta Feature")
    svc.set_enabled("ext-1", "beta", True)
    svc.add_to_allowlist("ext-1", "beta", "vip-user")
    assert svc.is_enabled("ext-1", "beta", "vip-user") is True
    assert svc.is_enabled("ext-1", "beta", "normal-user") is False

def test_blocklist():
    svc = ExtFeatureFlagSvcService()
    flag = svc.create("ext-1", "feature", "F")
    svc.set_rollout("ext-1", "feature", 100)
    flag.blocklist.add("banned-user")
    assert svc.is_enabled("ext-1", "feature", "banned-user") is False
