from app.services.app_marketplace_app_app_app_app_app_app_app_feature_reg import FeatureRegistry

def test_lifecycle():
    fr = FeatureRegistry()
    fr.register("dark_mode", enabled=False, tags=["ui"])
    fr.register("new_api", enabled=True, tags=["api"])
    assert not fr.is_enabled("dark_mode")
    fr.enable("dark_mode")
    assert fr.is_enabled("dark_mode")

def test_filter():
    fr = FeatureRegistry()
    fr.register("a", enabled=True, tags=["ui"])
    fr.register("b", enabled=False, tags=["api"])
    fr.register("c", enabled=True, tags=["ui"])
    assert len(fr.list_features(tag="ui")) == 2
    assert len(fr.list_features(enabled_only=True)) == 2
    assert fr.stats()["enabled"] == 2
