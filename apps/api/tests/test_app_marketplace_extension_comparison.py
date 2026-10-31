from app.services.app_marketplace_extension_comparison import ExtensionComparisonService


def test_compare():
    svc = ExtensionComparisonService()
    svc.register("ext-a", "Slack Bot", rating=4.8, installs=10000,
                 features=["notifications", "commands"], price_cents=999)
    svc.register("ext-b", "Discord Bot", rating=4.5, installs=8000,
                 features=["notifications", "webhooks"], price_cents=0)
    result = svc.compare(["ext-a", "ext-b"])
    assert len(result["extensions"]) == 2
    assert result["winners"]["rating"] == "ext-a"
    assert result["winners"]["price"] == "ext-b"


def test_feature_matrix():
    svc = ExtensionComparisonService()
    svc.register("a", "A", features=["auth", "api"])
    svc.register("b", "B", features=["api", "webhooks"])
    result = svc.compare(["a", "b"])
    assert result["feature_matrix"]["auth"]["a"] is True
    assert result["feature_matrix"]["auth"]["b"] is False
    assert result["feature_matrix"]["api"]["a"] is True
    assert result["feature_matrix"]["api"]["b"] is True


def test_recommendation():
    svc = ExtensionComparisonService()
    svc.register("a", "A", rating=4.9, installs=50000, features=["a", "b", "c"], price_cents=0)
    svc.register("b", "B", rating=3.0, installs=100, features=["a"], price_cents=4999)
    rec = svc.get_recommendation(["a", "b"])
    assert rec["recommended"] == "a"


def test_need_two():
    svc = ExtensionComparisonService()
    svc.register("a", "A")
    result = svc.compare(["a"])
    assert "error" in result
