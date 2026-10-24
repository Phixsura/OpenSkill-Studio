"""CLI generator — generate CLI scaffolding for apps."""

import re


def generate_cli_config(*, app_name: str, commands: list[dict]) -> dict:
    safe_name = re.sub(r"[^a-z0-9-]", "", app_name.lower().replace(" ", "-"))
    if not safe_name:
        return {"error": "Invalid app name for CLI"}
    cmd_defs = []
    for cmd in commands:
        args = []
        for arg in cmd.get("args", []):
            args.append({
                "name": arg["name"],
                "type": arg.get("type", "string"),
                "required": arg.get("required", False),
                "description": arg.get("description", ""),
            })
        cmd_defs.append({
            "name": cmd["name"],
            "description": cmd.get("description", ""),
            "args": args,
            "flags": cmd.get("flags", []),
        })
    return {
        "cli_name": safe_name,
        "bin_name": safe_name,
        "commands": cmd_defs,
        "total_commands": len(cmd_defs),
        "install_cmd": f"npm install -g @openskill/{safe_name}-cli",
        "usage": f"{safe_name} <command> [options]",
    }
