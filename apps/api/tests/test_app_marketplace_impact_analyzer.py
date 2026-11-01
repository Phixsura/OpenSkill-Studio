from app.services.app_marketplace_impact_analyzer import ImpactAnalyzer


def test_low_impact_update():
    ia = ImpactAnalyzer()
    ia.register_extension_data("ext-1", 2, 10, [])
    result = ia.analyze_update("ext-1")
    assert result.risk_level == "low"
    assert result.affected_orgs == 2


def test_high_impact_breaking():
    ia = ImpactAnalyzer()
    ia.register_extension_data("ext-2", 50, 500, ["dep-1", "dep-2"])
    result = ia.analyze_update("ext-2", breaking=True)
    assert result.risk_level in ("high", "critical")
    assert any("canary" in r.lower() for r in result.recommendations)
    assert any("dependent" in r.lower() for r in result.recommendations)


def test_deprecation():
    ia = ImpactAnalyzer()
    ia.register_extension_data("ext-3", 100, 1000, ["dep-a"])
    result = ia.analyze_deprecation("ext-3")
    assert result.change_type == "deprecate"
    assert any("90 days" in r for r in result.recommendations)
    assert any("migration" in r.lower() for r in result.recommendations)


def test_outage():
    ia = ImpactAnalyzer()
    ia.register_extension_data("ext-4", 200, 5000, ["a", "b", "c"])
    result = ia.analyze_outage("ext-4")
    assert result.risk_level == "critical"
    assert any("incident" in r.lower() for r in result.recommendations)
    assert any("cascading" in r.lower() for r in result.recommendations)


def test_compare():
    ia = ImpactAnalyzer()
    ia.register_extension_data("small", 5, 20, [])
    ia.register_extension_data("large", 500, 10000, ["x", "y"])
    comp = ia.compare_impact("small", "large")
    assert comp["higher_impact"] == "large"


def test_unknown_extension():
    ia = ImpactAnalyzer()
    result = ia.analyze_update("unknown")
    assert result.risk_level == "low"
    assert result.affected_orgs == 0
