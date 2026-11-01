from app.services.app_marketplace_newsletter import build_newsletter

def test_newsletter():
    n = build_newsletter(period="October 2026", new_apps=[{"name": "A"}], trending=[{"name": "B"}], updates=[{"name": "C"}])
    assert len(n["sections"]) == 3
    assert n["total_items"] == 3
    assert n["period"] == "October 2026"

def test_empty():
    n = build_newsletter(period="X", new_apps=[], trending=[], updates=[])
    assert n["total_items"] == 0
