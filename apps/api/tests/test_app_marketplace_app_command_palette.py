from app.services.app_marketplace_app_command_palette import search_commands, get_commands_by_category

def test_search():
    r = search_commands(query="deploy")
    assert r["total"] == 1
    assert r["commands"][0]["id"] == "deploy"

def test_search_empty():
    r = search_commands(query="")
    assert r["total"] == len(r["commands"]) or r["total"] >= 5

def test_search_category():
    r = search_commands(query="help")
    assert r["total"] >= 2

def test_by_category():
    r = get_commands_by_category()
    assert r["total_commands"] == 8
    assert len(r["categories"]) >= 3
