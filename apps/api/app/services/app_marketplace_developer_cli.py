"""Developer CLI — command definitions for the openskill CLI tool."""

CLI_COMMANDS = {
    "apps": {
        "list": {"description": "List your apps", "flags": ["--status", "--sort"]},
        "create": {"description": "Create a new app", "flags": ["--name", "--category", "--template"]},
        "deploy": {"description": "Deploy a version", "flags": ["--version", "--env", "--dry-run"]},
        "logs": {"description": "View app logs", "flags": ["--follow", "--level", "--since"]},
        "test": {"description": "Run tests in sandbox", "flags": ["--watch", "--coverage"]},
    },
    "webhooks": {
        "list": {"description": "List webhook endpoints", "flags": ["--app"]},
        "test": {"description": "Send test webhook", "flags": ["--event", "--url"]},
        "logs": {"description": "View delivery logs", "flags": ["--status", "--limit"]},
    },
    "auth": {
        "login": {"description": "Authenticate with OpenSkill", "flags": ["--token"]},
        "logout": {"description": "Sign out", "flags": []},
        "whoami": {"description": "Show current user", "flags": []},
    },
}


def get_cli_commands() -> dict:
    return CLI_COMMANDS


def get_command_help(*, group: str, command: str) -> dict | None:
    grp = CLI_COMMANDS.get(group)
    if not grp:
        return None
    cmd = grp.get(command)
    if not cmd:
        return None
    return {"group": group, "command": command, **cmd,
            "usage": f"openskill {group} {command} {' '.join(f'[{f}]' for f in cmd['flags'])}"}


def count_commands() -> int:
    return sum(len(cmds) for cmds in CLI_COMMANDS.values())
