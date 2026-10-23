from app.services.app_marketplace_app_app_modal_manager import create_modal, manage_modal_stack

def test_create():
    r = create_modal(modal_id="confirm", title="Confirm Delete", size="sm")
    assert r["modal_id"] == "confirm"
    assert r["size_class"] == "max-w-sm"

def test_invalid_size():
    r = create_modal(modal_id="x", title="X", size="huge")
    assert "error" in r

def test_push():
    r = manage_modal_stack(stack=["m1"], action="push", modal_id="m2")
    assert r["active"] == "m2"
    assert r["depth"] == 2

def test_pop():
    r = manage_modal_stack(stack=["m1", "m2"], action="pop")
    assert r["active"] == "m1"
    assert r["depth"] == 1

def test_clear():
    r = manage_modal_stack(stack=["m1", "m2"], action="clear")
    assert r["active"] is None
    assert r["depth"] == 0
