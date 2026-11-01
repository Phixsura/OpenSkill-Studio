from app.services.app_marketplace_app_developer_widget_library import list_widgets, get_widget, get_widget_categories

def test_list_all():
    assert len(list_widgets()) == 8

def test_filter():
    r = list_widgets(category="charts")
    assert len(r) == 2

def test_get():
    w = get_widget(widget_id="modal")
    assert w["name"] == "Modal Dialog"

def test_missing():
    assert get_widget(widget_id="nope") is None

def test_categories():
    c = get_widget_categories()
    assert len(c) >= 4
