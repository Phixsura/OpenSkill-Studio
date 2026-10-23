from app.services.app_marketplace_app_command_palette import search_commands, get_commands_by_category, get_recent_commands

def test_search():
    r = search_commands(query="log")
    assert any(c["id"] == "view_logs" for c in r)

def test_search_category():
    r = search_commands(query="debug")
    assert len(r) >= 2

def test_empty_query():
    r = search_commands(query="")
    assert len(r) == 6

def test_by_category():
    r = get_commands_by_category(category="config")
    assert len(r) >= 2

def test_recent():
    r = get_recent_commands(history=["deploy", "view_logs", "settings", "deploy"])
    assert r[0]["id"] == "deploy"
    assert len(r) == 3
