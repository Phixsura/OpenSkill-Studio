from app.services.app_marketplace_app_app_radio_group import build_radio_group

def test_basic():
    options = [{"value": "monthly", "label": "Monthly"}, {"value": "yearly", "label": "Yearly"}]
    r = build_radio_group(name="billing", label="Billing", options=options, selected="yearly")
    assert r["has_selection"]
    assert r["items"][1]["selected"]
    assert not r["items"][0]["selected"]

def test_none_selected():
    r = build_radio_group(name="x", label="X", options=[{"value": "a"}])
    assert not r["has_selection"]
