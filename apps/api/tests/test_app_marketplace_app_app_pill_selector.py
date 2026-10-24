from app.services.app_marketplace_app_app_pill_selector import build_pill_selector

def test_basic():
    options = [{"id": "a", "label": "Alpha"}, {"id": "b", "label": "Beta"}, {"id": "c", "label": "Gamma"}]
    r = build_pill_selector(options=options, selected=["a", "c"])
    assert r["selected_count"] == 2
    assert r["pills"][0]["selected"]
    assert not r["pills"][1]["selected"]

def test_max_reached():
    options = [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}, {"id": "c", "label": "C"}]
    r = build_pill_selector(options=options, selected=["a", "b"], max_select=2)
    assert not r["can_select_more"]
    assert r["pills"][2]["disabled"]  # c is disabled
