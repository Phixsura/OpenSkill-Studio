from app.services.app_marketplace_developer_cli import get_cli_commands, get_command_help, count_commands

def test_commands():
    c = get_cli_commands()
    assert "apps" in c
    assert "webhooks" in c
    assert "auth" in c

def test_help():
    h = get_command_help(group="apps", command="deploy")
    assert h is not None
    assert "--version" in h["usage"]

def test_unknown():
    assert get_command_help(group="nope", command="x") is None

def test_count():
    assert count_commands() >= 11
