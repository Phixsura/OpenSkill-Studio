"""CLI Scaffolder — generate CLI commands for extension development.

Produces the command structure and help text for the `osk` CLI tool
that developers use to create, test, publish, and manage extensions.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CLICommand:
    name: str
    description: str
    args: list[dict] = field(default_factory=list)  # [{name, required, description}]
    flags: list[dict] = field(default_factory=list)  # [{name, short, description, default}]
    subcommands: list[str] = field(default_factory=list)


class CLIScaffolder:
    """Generates CLI command definitions for the osk developer tool."""

    def __init__(self):
        self._commands: dict[str, CLICommand] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(CLICommand(
            "init", "Create a new extension project",
            args=[{"name": "name", "required": True, "description": "Extension name"}],
            flags=[
                {"name": "--template", "short": "-t", "description": "Template to use", "default": "connector"},
                {"name": "--author", "short": "-a", "description": "Author name", "default": ""},
            ],
        ))
        self.register(CLICommand(
            "dev", "Start local development server",
            flags=[
                {"name": "--port", "short": "-p", "description": "Dev server port", "default": "3100"},
                {"name": "--hot-reload", "short": None, "description": "Enable hot reload", "default": "true"},
            ],
        ))
        self.register(CLICommand(
            "test", "Run extension test suite",
            flags=[
                {"name": "--watch", "short": "-w", "description": "Watch mode", "default": "false"},
                {"name": "--coverage", "short": "-c", "description": "Show coverage", "default": "false"},
            ],
        ))
        self.register(CLICommand(
            "publish", "Publish extension to marketplace",
            flags=[
                {"name": "--version", "short": "-v", "description": "Version to publish", "default": ""},
                {"name": "--dry-run", "short": None, "description": "Validate without publishing", "default": "false"},
            ],
        ))
        self.register(CLICommand(
            "config", "Manage extension configuration",
            subcommands=["get", "set", "list", "delete"],
        ))

    def register(self, command: CLICommand) -> None:
        self._commands[command.name] = command

    def get_command(self, name: str) -> CLICommand | None:
        return self._commands.get(name)

    def list_commands(self) -> list[CLICommand]:
        return sorted(self._commands.values(), key=lambda c: c.name)

    def generate_help(self, command_name: str) -> str:
        """Generate help text for a command."""
        cmd = self._commands.get(command_name)
        if not cmd:
            return f"Unknown command: {command_name}"
        lines = [f"osk {cmd.name} — {cmd.description}", ""]
        if cmd.args:
            lines.append("Arguments:")
            for arg in cmd.args:
                req = " (required)" if arg["required"] else ""
                lines.append(f"  {arg['name']}{req}  {arg['description']}")
            lines.append("")
        if cmd.flags:
            lines.append("Flags:")
            for flag in cmd.flags:
                short = f", {flag['short']}" if flag.get("short") else ""
                default = f" (default: {flag['default']})" if flag.get("default") else ""
                lines.append(f"  {flag['name']}{short}  {flag['description']}{default}")
            lines.append("")
        if cmd.subcommands:
            lines.append("Subcommands:")
            for sub in cmd.subcommands:
                lines.append(f"  {sub}")
        return "\n".join(lines)

    def generate_completion(self, partial: str) -> list[str]:
        """Generate tab-completion suggestions."""
        return [c.name for c in self._commands.values() if c.name.startswith(partial)]
