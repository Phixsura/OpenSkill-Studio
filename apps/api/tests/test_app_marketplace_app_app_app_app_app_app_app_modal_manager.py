from app.services.app_marketplace_app_app_app_app_app_app_app_modal_manager import create_modal, manage_stack

def test_modal():
    m = create_modal(title="Confirm Delete", size="sm")
    assert m["title"] == "Confirm Delete"
    assert m["width"] == "400px"
    assert m["closable"]

def test_stack():
    s = manage_stack([
        create_modal(title="Settings"),
        create_modal(title="Confirm"),
    ])
    assert s["depth"] == 2
    assert s["top"]["title"] == "Confirm"
    assert s["has_overlay"]
