from app.services.app_marketplace_compatibility_checker import (
    CompatibilityChecker, CompatibilitySpec,
)


def test_compatible():
    cc = CompatibilityChecker(platform_version="2.0.0")
    cc.register_spec(CompatibilitySpec("ext-1", "1.0.0", "3.0.0"))
    result = cc.full_check("ext-1")
    assert result["compatible"] is True


def test_platform_too_old():
    cc = CompatibilityChecker(platform_version="0.9.0")
    cc.register_spec(CompatibilitySpec("ext-2", "1.0.0"))
    ok, msg = cc.check_platform_version("ext-2")
    assert ok is False
    assert "Requires platform >= 1.0.0" in msg


def test_platform_too_new():
    cc = CompatibilityChecker(platform_version="4.0.0")
    cc.register_spec(CompatibilitySpec("ext-3", "1.0.0", "3.0.0"))
    ok, msg = cc.check_platform_version("ext-3")
    assert ok is False
    assert "<= 3.0.0" in msg


def test_missing_apis():
    cc = CompatibilityChecker(available_apis=["extensions.v1"])
    cc.register_spec(CompatibilitySpec("ext-4", "1.0.0",
                                        required_apis=["extensions.v1", "billing.v2"]))
    ok, missing = cc.check_apis("ext-4")
    assert ok is False
    assert "billing.v2" in missing


def test_conflicts():
    cc = CompatibilityChecker()
    cc.register_spec(CompatibilitySpec("ext-5", "1.0.0",
                                        incompatible_extensions=["ext-old", "ext-rival"]))
    conflicts = cc.check_conflicts("ext-5", ["ext-old", "ext-other"])
    assert conflicts == ["ext-old"]


def test_full_check_all_fail():
    cc = CompatibilityChecker(platform_version="0.5.0", available_apis=[])
    cc.register_spec(CompatibilitySpec("ext-6", "1.0.0",
                                        required_apis=["extensions.v1"],
                                        incompatible_extensions=["bad"]))
    result = cc.full_check("ext-6", installed=["bad"])
    assert result["compatible"] is False
    assert result["platform_version"]["ok"] is False
    assert result["apis"]["ok"] is False
    assert "bad" in result["conflicts"]
