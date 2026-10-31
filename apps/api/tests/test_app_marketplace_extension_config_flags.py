from app.services.app_marketplace_extension_config_flags import ConfigFlagsService


def test_default_value():
    cf = ConfigFlagsService()
    cf.define("dark_mode", False)
    assert cf.is_enabled("dark_mode") is False


def test_override_hierarchy():
    cf = ConfigFlagsService()
    cf.define("feature_x", False)
    cf.set_override("feature_x", "env:prod", True)
    cf.set_override("feature_x", "tenant:acme", False)
    # Tenant overrides environment
    assert cf.evaluate("feature_x", {"environment": "prod", "tenant_id": "acme"}) is False
    # Without tenant, environment wins
    assert cf.evaluate("feature_x", {"environment": "prod"}) is True


def test_user_override_highest():
    cf = ConfigFlagsService()
    cf.define("beta", False)
    cf.set_override("beta", "env:prod", False)
    cf.set_override("beta", "user:vip-1", True)
    assert cf.is_enabled("beta", {"environment": "prod", "user_id": "vip-1"}) is True


def test_rollout_percentage():
    cf = ConfigFlagsService()
    cf.define("new_ui", True, rollout_pct=50)
    enabled = sum(1 for i in range(200)
                  if cf.is_enabled("new_ui", {"user_id": f"u-{i}"}))
    assert 60 < enabled < 140  # ~50%


def test_flag_dependency():
    cf = ConfigFlagsService()
    cf.define("base_feature", True)
    cf.define("advanced_feature", True, requires=["base_feature"])
    # With base enabled → advanced works
    assert cf.is_enabled("advanced_feature") is True
    # Disable base → advanced forced off
    cf.define("base_feature", False)
    assert cf.is_enabled("advanced_feature") is False


def test_string_flag():
    cf = ConfigFlagsService()
    cf.define("theme", "light", flag_type="string")
    cf.set_override("theme", "user:u1", "dark")
    assert cf.evaluate("theme", {"user_id": "u1"}) == "dark"
    assert cf.evaluate("theme") == "light"


def test_get_all():
    cf = ConfigFlagsService()
    cf.define("a", True)
    cf.define("b", False)
    cf.define("c", "hello", flag_type="string")
    all_flags = cf.get_all()
    assert all_flags == {"a": True, "b": False, "c": "hello"}


def test_audit_trail():
    cf = ConfigFlagsService()
    cf.define("flag", False)
    cf.set_override("flag", "env:prod", True)
    cf.set_override("flag", "env:staging", True)
    audit = cf.get_audit("flag")
    assert len(audit) == 2


def test_undefined_flag():
    cf = ConfigFlagsService()
    assert cf.evaluate("nonexistent") is None


def test_list_flags():
    cf = ConfigFlagsService()
    cf.define("a", True, rollout_pct=50)
    cf.define("b", "x", flag_type="string")
    flags = cf.list_flags()
    assert len(flags) == 2
