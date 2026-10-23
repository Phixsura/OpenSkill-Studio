from app.services.app_marketplace_responsive_layout import get_layout_config, should_lazy_load, get_image_sizes

def test_mobile():
    c = get_layout_config(page_type="marketplace_home", screen_width=375)
    assert c["device"] == "mobile"
    assert c["columns"] == 1
    assert not c["show_sidebar"]

def test_desktop():
    c = get_layout_config(page_type="marketplace_home", screen_width=1440)
    assert c["device"] == "desktop"
    assert c["columns"] == 4

def test_app_detail_tablet():
    c = get_layout_config(page_type="app_detail", screen_width=800)
    assert c["layout"] == "sidebar_right"

def test_lazy():
    assert should_lazy_load(position=10, viewport_items=6)
    assert not should_lazy_load(position=3, viewport_items=6)

def test_image_sizes():
    s = get_image_sizes(device="mobile")
    assert s["app_icon"] == 48
    assert s["hero"] == 640
