from app.services.app_marketplace_app_app_checkbox_group import build_checkbox_group

def test_basic():
    options = [{"value": "a", "label": "Alpha"}, {"value": "b", "label": "Beta"}, {"value": "c", "label": "Gamma"}]
    r = build_checkbox_group(name="tags", label="Tags", options=options, selected=["a", "c"])
    assert r["selected_count"] == 2
    assert r["items"][0]["checked"]
    assert not r["items"][1]["checked"]
    assert r["items"][2]["checked"]

def test_max_reached():
    options = [{"value": "a"}, {"value": "b"}, {"value": "c"}]
    r = build_checkbox_group(name="x", label="X", options=options, selected=["a", "b"], max_select=2)
    assert r["items"][2]["disabled"]  # c disabled because max reached
    assert r["valid"]
