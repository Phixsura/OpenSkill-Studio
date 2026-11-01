from app.services.app_marketplace_complete_marketplace_home import build_complete_marketplace_home

def test_home():
    p = build_complete_marketplace_home(
        featured_apps=[{"id": "f1"}], trending_apps=[{"id": "t1"}, {"id": "t2"}],
        new_apps=[{"id": "n1"}], categories=[{"key": "connector", "label": "Connectors"}],
        collections=[{"slug": "best"}],
        stats={"total_apps": 150, "total_developers": 40, "total_installs": 5000})
    assert p["page_type"] == "marketplace_home"
    assert len(p["sections"]) == 5
    assert "150" in p["hero"]["subtitle"]

def test_empty():
    p = build_complete_marketplace_home(
        featured_apps=[], trending_apps=[], new_apps=[], categories=[], collections=[], stats={})
    assert p["page_type"] == "marketplace_home"
