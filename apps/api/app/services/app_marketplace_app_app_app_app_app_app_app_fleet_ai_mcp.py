"""Fleet AI MCP — track Model Context Protocol servers."""
from __future__ import annotations
def fleet_ai_mcp(servers: list[dict]) -> dict:
    running = [s for s in servers if s.get("running", True)]
    tools_exposed = sum(s.get("tools", 0) for s in servers)
    resources = sum(s.get("resources", 0) for s in servers)
    calls_24h = sum(s.get("calls_24h", 0) for s in servers)
    return {"servers": len(servers), "running": len(running), "tools": tools_exposed,
            "resources": resources, "calls_24h": calls_24h}
