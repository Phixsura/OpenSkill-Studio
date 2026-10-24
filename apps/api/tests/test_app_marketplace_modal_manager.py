from app.services.app_marketplace_modal_manager import create_modal, get_modal_stack, get_standard_modal

def test_create():
    m = create_modal(modal_id="install", title="Install App", size="lg")
    assert m["size_class"] == "max-w-lg"
    assert not m["open"]

def test_invalid_size():
    m = create_modal(modal_id="x", title="X", size="huge")
    assert m["size"] == "md"

def test_stack():
    modals = [{"open": True, "overlay": True, "modal_id": "a"},
              {"open": False, "overlay": True, "modal_id": "b"},
              {"open": True, "overlay": False, "modal_id": "c"}]
    s = get_modal_stack(modals=modals)
    assert s["depth"] == 2
    assert s["top_modal"]["modal_id"] == "c"
    assert s["has_overlay"]

def test_standard():
    m = get_standard_modal(modal_type="install")
    assert m["title"] == "Install App"

def test_standard_unknown():
    assert get_standard_modal(modal_type="nope") is None
