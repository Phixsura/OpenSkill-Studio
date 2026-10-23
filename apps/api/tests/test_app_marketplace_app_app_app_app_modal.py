from app.services.app_marketplace_app_app_app_app_modal import build_modal_config

def test_modal():
    r = build_modal_config(title="Delete App", size="sm", danger=True)
    assert r["title"] == "Delete App"
    assert r["size_class"] == "max-w-sm"
    assert r["danger"]
    assert r["closable"]

def test_defaults():
    r = build_modal_config(title="Settings")
    assert r["size"] == "md"
    assert r["has_footer"]
