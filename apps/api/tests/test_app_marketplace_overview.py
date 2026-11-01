from app.services.app_marketplace_overview import build_marketplace_overview

def test_overview():
    o = build_marketplace_overview(featured=[{"id": "f1"}], trending=[{"id": "t1"}],
        recent=[{"id": "r1"}], categories=[{"key": "connector"}], stats={"total": 100})
    assert len(o["sections"]) == 3
    assert o["stats"]["total"] == 100

def test_limits():
    o = build_marketplace_overview(featured=[{}]*20, trending=[{}]*20, recent=[{}]*20, categories=[], stats={})
    assert len(o["featured"]) == 6
    assert len(o["trending"]) == 10
    assert len(o["recent"]) == 12
