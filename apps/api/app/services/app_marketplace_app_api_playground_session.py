"""API playground session — persistent playground sessions with history."""

from datetime import datetime, timezone


def create_session(*, developer_id: str, app_id: str, base_url: str) -> dict:
    return {"developer_id": developer_id, "app_id": app_id, "base_url": base_url,
            "history": [], "variables": {}, "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()}


def add_variable(*, session: dict, key: str, value: str) -> dict:
    vars = dict(session.get("variables", {}))
    vars[key] = value
    return {**session, "variables": vars}


def interpolate_variables(*, template: str, variables: dict) -> str:
    result = template
    for k, v in variables.items():
        result = result.replace(f"{{{{{k}}}}}", v)
    return result


def add_to_history(*, session: dict, request: dict, response: dict) -> dict:
    entry = {"request": request, "response": response, "timestamp": datetime.now(timezone.utc).isoformat()}
    history = list(session.get("history", []))
    history.append(entry)
    return {**session, "history": history[-50:]}  # Keep last 50
