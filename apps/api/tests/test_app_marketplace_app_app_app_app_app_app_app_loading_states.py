from app.services.app_marketplace_app_app_app_app_app_app_app_loading_states import get_loading_config, should_show_loader, list_contexts

def test_config():
    c = get_loading_config("button")
    assert c["type"] == "spinner"
    assert c["delay_ms"] == 0

def test_should_show():
    assert not should_show_loader(elapsed_ms=100, context="page")  # delay=200
    assert should_show_loader(elapsed_ms=250, context="page")
    assert should_show_loader(elapsed_ms=0, context="button")  # delay=0

def test_list():
    contexts = list_contexts()
    assert len(contexts) == 6
