from app.services.app_marketplace_app_app_app_app_app_app_app_command_palette import CommandPalette

def test_palette():
    cp = CommandPalette()
    cp.register(id="dashboard", title="Go to Dashboard", shortcut="⌘D", category="navigation", url="/dashboard")
    cp.register(id="settings", title="Open Settings", shortcut="⌘,", category="navigation", url="/settings")
    cp.register(id="deploy", title="Deploy to Production", shortcut="⌘⇧D", category="actions")
    cp.register(id="search", title="Search Everything", shortcut="⌘K", category="actions")
    r = cp.search("dash")
    assert len(r) == 1
    assert r[0]["id"] == "dashboard"
    r2 = cp.search("to")
    assert len(r2) == 2  # "Go to Dashboard" and "Deploy to Production"
    cats = cp.by_category()
    assert len(cats["navigation"]) == 2
    assert len(cats["actions"]) == 2
