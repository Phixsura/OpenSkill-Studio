from app.services.app_marketplace_extension_cmd_palette import ExtCmdPaletteService

def test_search():
    svc = ExtCmdPaletteService()
    results = svc.search("deploy")
    assert len(results) == 1
    assert results[0].command_id == "action-deploy"

def test_by_category():
    svc = ExtCmdPaletteService()
    nav = svc.get_by_category("navigation")
    assert len(nav) == 3

def test_register():
    svc = ExtCmdPaletteService()
    svc.register("custom", "Custom Action", "action", "⌘X", "⚡", "/custom")
    results = svc.search("custom")
    assert len(results) == 1

def test_all():
    svc = ExtCmdPaletteService()
    assert len(svc.get_all()) >= 8
