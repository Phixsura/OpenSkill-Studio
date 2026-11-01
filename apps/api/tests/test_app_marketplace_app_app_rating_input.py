from app.services.app_marketplace_app_app_rating_input import build_rating_input

def test_rating():
    r = build_rating_input(current_value=4)
    assert r["display"] == "★★★★☆"
    assert r["label"] == "Very Good"
    assert r["stars"][3]["filled"]
    assert not r["stars"][4]["filled"]

def test_empty():
    r = build_rating_input(current_value=0)
    assert r["display"] == "☆☆☆☆☆"
    assert r["label"] == ""

def test_full():
    r = build_rating_input(current_value=5)
    assert r["display"] == "★★★★★"
    assert r["label"] == "Excellent"
