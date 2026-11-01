from app.services.app_marketplace_cli_scaffolder import CLIScaffolder, CLICommand


def test_default_commands():
    cli = CLIScaffolder()
    commands = cli.list_commands()
    names = [c.name for c in commands]
    assert "init" in names
    assert "dev" in names
    assert "test" in names
    assert "publish" in names
    assert "config" in names


def test_get_command():
    cli = CLIScaffolder()
    cmd = cli.get_command("init")
    assert cmd is not None
    assert cmd.args[0]["name"] == "name"
    assert any(f["name"] == "--template" for f in cmd.flags)


def test_generate_help():
    cli = CLIScaffolder()
    help_text = cli.generate_help("publish")
    assert "osk publish" in help_text
    assert "--version" in help_text
    assert "--dry-run" in help_text


def test_generate_help_unknown():
    cli = CLIScaffolder()
    assert "Unknown command" in cli.generate_help("nonexistent")


def test_register_custom():
    cli = CLIScaffolder()
    cli.register(CLICommand("deploy", "Deploy to production",
                             flags=[{"name": "--env", "short": "-e", "description": "Target env", "default": "staging"}]))
    assert cli.get_command("deploy") is not None
    assert "deploy" in cli.generate_help("deploy")


def test_completion():
    cli = CLIScaffolder()
    assert "config" in cli.generate_completion("con")
    assert "publish" in cli.generate_completion("pu")
    assert cli.generate_completion("xyz") == []
