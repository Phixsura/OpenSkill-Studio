"""API playground — interactive API request builder."""

import html
import json
from urllib.parse import urlparse

METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]


def build_request(*, method: str, url: str, headers: dict | None = None,
                   body: str | None = None) -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        return {"error": "Invalid URL scheme"}
    if method.upper() not in METHODS:
        return {"error": f"Invalid method: {method}"}
    safe_headers = {html.escape(k): html.escape(v) for k, v in (headers or {}).items()}
    curl = f"curl -X {method.upper()} '{url}'"
    for k, v in safe_headers.items():
        curl += f" \\\n  -H '{k}: {v}'"
    if body and method.upper() in ("POST", "PUT", "PATCH"):
        curl += f" \\\n  -d '{html.escape(body)}'"
    return {"method": method.upper(), "url": url, "headers": safe_headers,
            "body": body, "curl": curl, "has_body": body is not None}


def simulate_response(*, status: int = 200, body: dict | None = None,
                        latency_ms: int = 45) -> dict:
    return {"status": status, "status_text": "OK" if 200 <= status < 300 else "Error",
            "body": json.dumps(body or {}, indent=2),
            "latency_ms": latency_ms, "success": 200 <= status < 300}
