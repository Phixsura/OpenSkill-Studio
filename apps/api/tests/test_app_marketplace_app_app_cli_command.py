from app.services.app_marketplace_app_app_cli_command import get_command_help, build_cli_reference

def test_help():
    r = get_command_help(command="deploy")
    assert r["command"] == "deploy"
    assert "--force" in r["flags"]

def test_unknown():
    r = get_command_help(command="nonexistent")
    assert "error" in r

def test_reference():
    r = build_cli_reference()
    assert r["total"] == 5
    assert any(c["command"] == "init" for c in r["commands"])
