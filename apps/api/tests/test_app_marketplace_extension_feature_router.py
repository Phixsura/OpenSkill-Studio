from app.services.app_marketplace_extension_feature_router import FeatureRouterService


def test_simple_routing():
    fr = FeatureRouterService()
    fr.define_route("new_ui", [("control", "/old-ui", 50), ("treatment", "/new-ui", 50)])
    result = fr.route("new_ui", user_id="user-1")
    assert result["variant"] in ("control", "treatment")
    assert result["feature"] == "new_ui"


def test_deterministic():
    fr = FeatureRouterService()
    fr.define_route("test", [("a", "/a", 50), ("b", "/b", 50)])
    r1 = fr.route("test", user_id="user-42")
    r2 = fr.route("test", user_id="user-42")
    assert r1["variant"] == r2["variant"]  # same user → same variant


def test_weight_distribution():
    fr = FeatureRouterService()
    fr.define_route("split", [("canary", "/canary", 10), ("stable", "/stable", 90)])
    counts = {"canary": 0, "stable": 0}
    for i in range(1000):
        r = fr.route("split", user_id=f"u-{i}")
        counts[r["variant"]] += 1
    assert counts["canary"] < 200  # ~10%
    assert counts["stable"] > 800  # ~90%


def test_disabled_feature():
    fr = FeatureRouterService()
    fr.define_route("beta", [("new", "/new", 100)], fallback="/old")
    fr.toggle("beta", False)
    result = fr.route("beta", user_id="u1")
    assert result["target"] == "/old"
    assert result["variant"] == "fallback"


def test_user_override():
    fr = FeatureRouterService()
    fr.define_route("ui", [("a", "/a", 50), ("b", "/b", 50)])
    fr.set_override("ui", "vip-user", "b")
    result = fr.route("ui", user_id="vip-user")
    assert result["variant"] == "b"
    assert result["override"] is True


def test_clear_override():
    fr = FeatureRouterService()
    fr.define_route("f", [("x", "/x", 100)])
    fr.set_override("f", "u1", "x")
    fr.clear_override("f", "u1")
    result = fr.route("f", user_id="u1")
    assert result.get("override") is not True


def test_metrics():
    fr = FeatureRouterService()
    fr.define_route("test", [("a", "/a", 50), ("b", "/b", 50)])
    for i in range(100):
        fr.route("test", user_id=f"u-{i}")
    metrics = fr.get_metrics("test")
    assert metrics["total_routed"] == 100
    assert sum(metrics["distribution"].values()) > 99  # ~100%


def test_undefined_feature():
    fr = FeatureRouterService()
    result = fr.route("nonexistent")
    assert result["target"] == "default"


def test_single_variant():
    fr = FeatureRouterService()
    fr.define_route("all_new", [("new", "/new-page", 100)])
    result = fr.route("all_new", user_id="anyone")
    assert result["variant"] == "new"
    assert result["target"] == "/new-page"
