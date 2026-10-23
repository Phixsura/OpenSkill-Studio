from app.services.app_marketplace_app_app_app_app_app_app_app_a11y_checker import check_color_contrast, check_component

def test_contrast():
    r = check_color_contrast(fg="#000000", bg="#FFFFFF")
    assert r["ratio"] == 21.0
    assert r["aa"]
    assert r["aaa"]
    assert r["level"] == "AAA"

def test_low_contrast():
    r = check_color_contrast(fg="#777777", bg="#999999")
    assert not r["aa"]
    assert r["level"] == "Fail"

def test_component_pass():
    r = check_component({"name": "submit_btn", "type": "button", "label": "Submit"})
    assert r["passes"]

def test_component_fail():
    r = check_component({"name": "icon_btn", "type": "button"})
    assert not r["passes"]
    assert r["issue_count"] >= 1
