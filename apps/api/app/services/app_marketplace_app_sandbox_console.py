"""Sandbox console — interactive REPL for testing app code in sandbox."""

from datetime import datetime, timezone


def create_console_session(*, app_id: str, developer_id: str, language: str = "javascript") -> dict:
    supported = {"javascript", "typescript", "python"}
    if language not in supported:
        return {"error": f"Unsupported language. Use: {', '.join(sorted(supported))}"}
    return {"app_id": app_id, "developer_id": developer_id, "language": language,
            "status": "active", "history": [], "error": None,
            "created_at": datetime.now(timezone.utc).isoformat()}


def execute_command(*, session: dict, code: str) -> dict:
    if len(code) > 10000:
        return {"error": "Code too long (max 10,000 chars)", "output": None}
    # Simulated execution
    return {
        "input": code, "output": f"[simulated output for: {code[:50]}]",
        "execution_time_ms": 12, "error": None,
    }


def build_console_history(*, commands: list[dict]) -> list[dict]:
    return [{"index": i, "input": c.get("input", ""), "output": c.get("output", ""),
             "error": c.get("error")} for i, c in enumerate(commands)]
