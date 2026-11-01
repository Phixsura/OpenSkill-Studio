from app.services.app_marketplace_feature_matrix import (
    FeatureMatrixBuilder, ExtensionFeatures,
)


def _setup() -> FeatureMatrixBuilder:
    fm = FeatureMatrixBuilder()
    fm.define_feature("webhooks", "Webhooks", "Integration")
    fm.define_feature("scheduling", "Scheduling", "Integration")
    fm.define_feature("analytics", "Analytics", "Insights")
    fm.define_feature("dark_mode", "Dark Mode", "UI")

    fm.register_extension(ExtensionFeatures("slack", "Slack Bot",
        {"webhooks": True, "scheduling": True, "analytics": False, "dark_mode": True}))
    fm.register_extension(ExtensionFeatures("teams", "Teams Bot",
        {"webhooks": True, "scheduling": False, "analytics": True, "dark_mode": False}))
    return fm


def test_build_matrix():
    fm = _setup()
    matrix = fm.build_matrix()
    assert len(matrix["extensions"]) == 2
    assert len(matrix["groups"]) == 3  # Integration, Insights, UI


def test_build_specific_extensions():
    fm = _setup()
    matrix = fm.build_matrix(["slack"])
    assert len(matrix["extensions"]) == 1


def test_unique_features():
    fm = _setup()
    unique = fm.get_unique_features("slack")
    assert "scheduling" in unique
    assert "dark_mode" in unique


def test_missing_features():
    fm = _setup()
    missing = fm.get_missing_features("teams")
    assert "scheduling" in missing
    assert "dark_mode" in missing


def test_feature_coverage():
    fm = _setup()
    assert fm.get_feature_coverage("slack") == 75.0  # 3/4
    assert fm.get_feature_coverage("teams") == 50.0  # 2/4
