"""Extension postMessage protocol — define message types for iframe communication."""

INBOUND_MESSAGES = {
    "api_request": {"required": ["method", "path"], "optional": ["body", "params"]},
    "ui_resize": {"required": ["width", "height"]},
    "ui_navigate": {"required": ["path"]},
    "ui_toast": {"required": ["message"], "optional": ["type"]},
    "ready": {"required": []},
}

OUTBOUND_MESSAGES = {
    "context": {"fields": ["orgId", "userId", "surface", "entityId", "permissions"]},
    "api_response": {"fields": ["requestId", "status", "data", "error"]},
    "theme": {"fields": ["mode", "colors"]},
}


def validate_inbound_message(msg: dict) -> list[str]:
    msg_type = msg.get("type")
    if msg_type not in INBOUND_MESSAGES:
        return [f"Unknown message type: {msg_type}"]
    schema = INBOUND_MESSAGES[msg_type]
    errors = []
    for field in schema["required"]:
        if field not in msg.get("payload", {}):
            errors.append(f"Missing field: {field}")
    return errors


def build_context_message(*, org_id: str, user_id: str, surface: str, permissions: list[str]) -> dict:
    return {"type": "context", "payload": {"orgId": org_id, "userId": user_id,
            "surface": surface, "permissions": permissions}}
