"""CLI tool manager — manage CLI tools and their versions."""
from __future__ import annotations


def list_tools(tools: list[dict]) -> dict:
    installed = sum(1 for t in tools if t.get("installed"))
    outdated = sum(1 for t in tools if t.get("installed") and t.get("update_available"))
    return {"tools": tools, "total": len(tools), "installed": installed,
            "outdated": outdated, "up_to_date": installed - outdated}


def check_tool(name: str, current_version: str, latest_version: str) -> dict:
    update_available = current_version != latest_version
    major_update = current_version.split(".")[0] != latest_version.split(".")[0] if update_available else False
    return {"name": name, "current": current_version, "latest": latest_version,
            "update_available": update_available, "major_update": major_update}


def install_report(actions: list[dict]) -> dict:
    installed = sum(1 for a in actions if a.get("action") == "install")
    updated = sum(1 for a in actions if a.get("action") == "update")
    failed = sum(1 for a in actions if a.get("status") == "failed")
    return {"total_actions": len(actions), "installed": installed,
            "updated": updated, "failed": failed,
            "success": failed == 0}
