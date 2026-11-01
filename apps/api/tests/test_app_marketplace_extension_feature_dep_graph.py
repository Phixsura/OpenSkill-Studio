from app.services.app_marketplace_extension_feature_dep_graph import FeatureDepGraphService


def test_add_and_dependency():
    fdg = FeatureDepGraphService()
    fdg.add_feature("auth")
    fdg.add_feature("user_profile", description="User profiles")
    fdg.add_dependency("user_profile", "auth")
    impact = fdg.impact_analysis("auth")
    assert "user_profile" in impact["directly_affected"]


def test_cascading_impact():
    fdg = FeatureDepGraphService()
    for f in ["db", "cache", "api", "dashboard", "reports"]:
        fdg.add_feature(f)
    fdg.add_dependency("api", "db")
    fdg.add_dependency("api", "cache")
    fdg.add_dependency("dashboard", "api")
    fdg.add_dependency("reports", "api")
    impact = fdg.impact_analysis("db")
    assert "api" in impact["total_affected"]
    assert "dashboard" in impact["total_affected"]
    assert impact["blast_radius"] == 3  # api, dashboard, reports


def test_safe_disable_order():
    fdg = FeatureDepGraphService()
    for f in ["base", "middle", "top"]:
        fdg.add_feature(f)
    fdg.add_dependency("middle", "base")
    fdg.add_dependency("top", "middle")
    order = fdg.safe_disable_order(["base", "middle", "top"])
    assert order.index("top") < order.index("middle")
    assert order.index("middle") < order.index("base")


def test_coupling_score():
    fdg = FeatureDepGraphService()
    for f in ["core", "a", "b", "c", "d"]:
        fdg.add_feature(f)
    for dep in ["a", "b", "c", "d"]:
        fdg.add_dependency(dep, "core")
    score = fdg.coupling_score("core")
    assert score["fan_in"] == 4  # 4 things depend on core
    assert score["level"] == "medium"  # 4 fan_in + 0 fan_out = 4


def test_orphans():
    fdg = FeatureDepGraphService()
    fdg.add_feature("core")
    fdg.add_feature("used")
    fdg.add_feature("orphan")
    fdg.add_dependency("used", "core")
    orphans = fdg.find_orphans()
    assert "orphan" in orphans
    assert "used" in orphans  # nothing depends on "used" either
    assert "core" not in orphans  # "used" depends on core


def test_roots():
    fdg = FeatureDepGraphService()
    fdg.add_feature("foundation")
    fdg.add_feature("layer1")
    fdg.add_feature("layer2")
    fdg.add_dependency("layer1", "foundation")
    fdg.add_dependency("layer2", "layer1")
    roots = fdg.find_roots()
    assert roots == ["foundation"]


def test_layers():
    fdg = FeatureDepGraphService()
    for f in ["db", "cache", "api", "ui"]:
        fdg.add_feature(f)
    fdg.add_dependency("api", "db")
    fdg.add_dependency("api", "cache")
    fdg.add_dependency("ui", "api")
    layers = fdg.get_layers()
    assert layers[0] == ["cache", "db"]  # depth 0
    assert layers[1] == ["api"]          # depth 1
    assert layers[2] == ["ui"]           # depth 2


def test_critical_breaks():
    fdg = FeatureDepGraphService()
    fdg.add_feature("auth")
    fdg.add_feature("login")
    fdg.add_feature("signup")
    fdg.add_dependency("login", "auth")
    fdg.add_dependency("signup", "auth")
    impact = fdg.impact_analysis("auth")
    # login and signup have no other deps → they critically break
    assert "login" in impact["critical_breaks"]
    assert "signup" in impact["critical_breaks"]
