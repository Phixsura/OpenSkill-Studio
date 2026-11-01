"""Extension CLI Tool Registry — register and discover CLI tools for extensions."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CliCommand:
    name: str
    description: str
    usage: str
    flags: list[dict] = field(default_factory=list)  # [{name, short, description, required}]


@dataclass
class CliTool:
    tool_id: str
    extension_id: str
    name: str
    version: str
    commands: list[CliCommand] = field(default_factory=list)
    install_cmd: str = ""


class ExtCliRegistryService:
    def __init__(self):
        self._tools: dict[str, CliTool] = {}

    def register(self, extension_id: str, name: str, version: str,
                 install_cmd: str = "") -> CliTool:
        tool_id = f"{extension_id}:{name}"
        tool = CliTool(tool_id=tool_id, extension_id=extension_id,
                       name=name, version=version, install_cmd=install_cmd)
        self._tools[tool_id] = tool
        return tool

    def add_command(self, tool_id: str, name: str, description: str,
                    usage: str, flags: list[dict] | None = None) -> bool:
        tool = self._tools.get(tool_id)
        if not tool:
            return False
        tool.commands.append(CliCommand(name=name, description=description,
                                        usage=usage, flags=flags or []))
        return True

    def search(self, query: str) -> list[CliTool]:
        q = query.lower()
        return [t for t in self._tools.values()
                if q in t.name.lower() or any(q in c.name.lower() for c in t.commands)]

    def get_all(self) -> list[CliTool]:
        return list(self._tools.values())

    def get(self, tool_id: str) -> CliTool | None:
        return self._tools.get(tool_id)

    def generate_help(self, tool_id: str) -> str:
        tool = self._tools.get(tool_id)
        if not tool:
            return ""
        lines = [f"{tool.name} v{tool.version}", ""]
        if tool.install_cmd:
            lines.append(f"Install: {tool.install_cmd}\n")
        lines.append("Commands:")
        for cmd in tool.commands:
            lines.append(f"  {cmd.usage:<30} {cmd.description}")
        return "\n".join(lines)
