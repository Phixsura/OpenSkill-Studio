"""CLI command — CLI tool command registry and help generator."""

import html

COMMANDS = {
    "init": {"description": "Initialize a new app project", "usage": "osk init <app-name> [--template=<tmpl>]",
             "flags": ["--template", "--runtime", "--no-git"]},
    "deploy": {"description": "Deploy the current app", "usage": "osk deploy [--env=<env>] [--force]",
               "flags": ["--env", "--force", "--dry-run"]},
    "logs": {"description": "Stream app logs", "usage": "osk logs [--follow] [--lines=<n>]",
             "flags": ["--follow", "--lines", "--filter"]},
    "status": {"description": "Show deployment status", "usage": "osk status [<app-name>]",
               "flags": ["--json", "--verbose"]},
    "config": {"description": "Manage app configuration", "usage": "osk config <get|set|list> [key] [value]",
               "flags": ["--env", "--json"]},
}


def get_command_help(*, command: str) -> dict:
    cmd = COMMANDS.get(command)
    if not cmd:
        return {"error": f"Unknown command: {command}", "available": list(COMMANDS.keys())}
    return {"command": command, **cmd, "flag_count": len(cmd["flags"])}


def build_cli_reference() -> dict:
    items = [{"command": k, "description": v["description"], "usage": v["usage"],
              "flag_count": len(v["flags"])} for k, v in COMMANDS.items()]
    return {"commands": items, "total": len(items)}
