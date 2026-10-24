"""JSON-RPC protocol — build/parse JSON-RPC 2.0 messages for sandbox IPC."""

import json


def build_request(method: str, params: dict | None = None, id: int = 1) -> str:
    """Build a JSON-RPC 2.0 request."""
    msg = {"jsonrpc": "2.0", "method": method, "id": id}
    if params is not None:
        msg["params"] = params
    return json.dumps(msg)


def build_response(result: object, id: int = 1) -> str:
    """Build a JSON-RPC 2.0 success response."""
    return json.dumps({"jsonrpc": "2.0", "result": result, "id": id})


def build_error(code: int, message: str, id: int | None = 1) -> str:
    """Build a JSON-RPC 2.0 error response."""
    return json.dumps({"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": id})


def parse_message(raw: str) -> dict:
    """Parse a JSON-RPC message. Returns parsed dict or error."""
    try:
        msg = json.loads(raw)
    except json.JSONDecodeError:
        return {"valid": False, "error": "Invalid JSON"}
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
        return {"valid": False, "error": "Not JSON-RPC 2.0"}
    return {"valid": True, "message": msg, "is_request": "method" in msg, "is_response": "result" in msg or "error" in msg}
