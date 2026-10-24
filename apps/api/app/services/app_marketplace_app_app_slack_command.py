"""Slack command — slash command parser and dispatcher."""

import html
import hmac
import hashlib
import secrets

HMAC_KEY = secrets.token_bytes(32)

COMMANDS = {
    "/status": {"description": "Check app status", "usage": "/status [app_name]"},
    "/deploy": {"description": "Deploy an app", "usage": "/deploy <app_name> <version>"},
    "/rollback": {"description": "Rollback deployment", "usage": "/rollback <app_name>"},
    "/logs": {"description": "View recent logs", "usage": "/logs <app_name> [--lines=N]"},
    "/help": {"description": "Show available commands", "usage": "/help"},
}


def parse_command(*, text: str) -> dict:
    parts = text.strip().split()
    if not parts:
        return {"error": "Empty command"}
    cmd = parts[0].lower()
    args = parts[1:]
    if cmd not in COMMANDS:
        return {"error": f"Unknown command: {cmd}", "available": list(COMMANDS.keys())}
    info = COMMANDS[cmd]
    return {"command": cmd, "args": args, "description": info["description"],
            "usage": info["usage"], "valid": True}


def verify_slack_signature(*, body: str, timestamp: str, signature: str,
                             signing_secret: str) -> bool:
    base = f"v0:{timestamp}:{body}"
    expected = "v0=" + hmac.new(signing_secret.encode(), base.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def list_commands() -> list[dict]:
    return [{"command": k, **v} for k, v in COMMANDS.items()]
