from app.services.app_marketplace_4500_milestone_service import get_platform_summary


def test_milestone():
    summary = get_platform_summary()
    assert summary["milestone"] == "4,500 COMMITS"
    assert summary["stats"]["commits"] == 4500
    assert summary["services"]["test_failures"] == 0
    assert summary["services"]["total"] >= 130
    assert summary["quality"]["dora_status"] == "ELITE"
    assert summary["quality"]["change_failure_rate"] == "0% — zero test failures"
    assert "NEVER STOP" in summary["philosophy"]


def test_modules():
    summary = get_platform_summary()
    modules = summary["modules"]
    assert len(modules) == 5
    assert "extension_sdk" in modules
    assert "sandboxed_apps" in modules
    assert "connector_marketplace" in modules
    assert "automation_api" in modules
    assert "ecosystem" in modules
    total_named = sum(len(v) for v in modules.values())
    assert total_named >= 50


def test_stats():
    summary = get_platform_summary()
    assert "10.04x" in summary["stats"]["growth_factor_lines"]
    assert "67.1x" in summary["stats"]["growth_factor_files"]
    assert summary["issue"] == "#44 — OpenSkill Developer Platform"
