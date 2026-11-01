from app.services.app_marketplace_extension_sandbox_feature_gate import (
    SandboxFeatureGateService, Tier,
)


def test_define_and_check():
    svc = SandboxFeatureGateService()
    svc.define_gate("network_access", Tier.STARTER)
    svc.set_tier("sb-1", Tier.PRO)
    result = svc.is_enabled("sb-1", "network_access")
    assert result["enabled"] is True


def test_tier_too_low():
    svc = SandboxFeatureGateService()
    svc.define_gate("gpu_access", Tier.ENTERPRISE)
    svc.set_tier("sb-1", Tier.FREE)
    result = svc.is_enabled("sb-1", "gpu_access")
    assert result["enabled"] is False
    assert "enterprise" in result["reason"].lower()


def test_free_tier_default():
    svc = SandboxFeatureGateService()
    svc.define_gate("basic_io", Tier.FREE)
    # No tier set = defaults to FREE
    result = svc.is_enabled("sb-1", "basic_io")
    assert result["enabled"] is True


def test_admin_override():
    svc = SandboxFeatureGateService()
    svc.define_gate("premium", Tier.ENTERPRISE)
    svc.set_tier("sb-1", Tier.FREE)
    svc.set_override("sb-1", "premium", True)
    result = svc.is_enabled("sb-1", "premium")
    assert result["enabled"] is True
    assert "override" in result["reason"]


def test_admin_override_deny():
    svc = SandboxFeatureGateService()
    svc.define_gate("basic", Tier.FREE)
    svc.set_override("sb-1", "basic", False)
    result = svc.is_enabled("sb-1", "basic")
    assert result["enabled"] is False


def test_clear_override():
    svc = SandboxFeatureGateService()
    svc.define_gate("feat", Tier.PRO)
    svc.set_override("sb-1", "feat", True)
    svc.clear_override("sb-1", "feat")
    svc.set_tier("sb-1", Tier.FREE)
    result = svc.is_enabled("sb-1", "feat")
    assert result["enabled"] is False  # back to tier check


def test_get_available():
    svc = SandboxFeatureGateService()
    svc.define_gate("basic", Tier.FREE)
    svc.define_gate("advanced", Tier.PRO)
    svc.define_gate("premium", Tier.ENTERPRISE)
    svc.set_tier("sb-1", Tier.PRO)
    available = svc.get_available_features("sb-1")
    assert "basic" in available
    assert "advanced" in available
    assert "premium" not in available


def test_global_disable():
    svc = SandboxFeatureGateService()
    svc.define_gate("feat", Tier.FREE)
    svc.disable_gate("feat")
    result = svc.is_enabled("sb-1", "feat")
    assert result["enabled"] is False
    assert "globally" in result["reason"]


def test_undefined_feature():
    svc = SandboxFeatureGateService()
    result = svc.is_enabled("sb-1", "nonexistent")
    assert result["enabled"] is False
