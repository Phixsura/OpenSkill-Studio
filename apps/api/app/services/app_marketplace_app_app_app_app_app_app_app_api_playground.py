"""API playground — interactive API testing console."""
from __future__ import annotations
import html
import time


def build_request(method: str, path: str, headers: dict | None = None,
                   body: str = "") -> dict:
    return {"method": method.upper(), "path": path,
            "headers": headers or {"Content-Type": "application/json"},
            "body": body, "built_at": time.time()}


def simulate_response(request: dict) -> dict:
    method = request["method"]
    status_map = {"GET": 200, "POST": 201, "PUT": 200, "PATCH": 200, "DELETE": 204}
    status = status_map.get(method, 200)
    body = {"message": f"Simulated {method} response", "path": request["path"]}
    return {"status": status, "headers": {"Content-Type": "application/json"},
            "body": body, "response_ms": 42}


def save_to_history(request: dict, response: dict) -> dict:
    return {"method": request["method"], "path": request["path"],
            "status": response["status"], "response_ms": response["response_ms"],
            "timestamp": time.time()}
