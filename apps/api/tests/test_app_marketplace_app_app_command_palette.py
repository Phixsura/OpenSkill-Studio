from app.services.app_marketplace_app_app_command_palette import build_command_palette

CMDS = [
    {"id": "1", "label": "New App", "shortcut": "Ctrl+N", "category": "File"},
    {"id": "2", "label": "Settings", "shortcut": "Ctrl+,", "category": "Edit"},
    {"id": "3", "label": "Deploy", "icon": "🚀", "category": "Actions"},
]

def test_no_query():
    r = build_command_palette(commands=CMDS)
    assert r["total"] == 3

def test_filter():
    r = build_command_palette(commands=CMDS, query="deploy")
    assert r["total"] == 1
    assert r["results"][0]["icon"] == "🚀"

def test_category_filter():
    r = build_command_palette(commands=CMDS, query="file")
    assert r["total"] == 1
    assert r["results"][0]["label"] == "New App"
