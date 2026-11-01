"""API request inspector — inspect and debug API requests."""
from __future__ import annotations
import html


def inspect_request(method: str, path: str, headers: dict,
                     body: str = "", query_params: dict | None = None) -> dict:
    content_type = headers.get("content-type", headers.get("Content-Type", ""))
    auth = "bearer" if "authorization" in {k.lower() for k in headers} else "none"
    body_size = len(body.encode())
    return {"method": method.upper(), "path": path,
            "header_count": len(headers), "content_type": content_type,
            "auth_type": auth, "body_size": body_size,
            "query_params": query_params or {},
            "param_count": len(query_params or {})}


def request_diff(req_a: dict, req_b: dict) -> dict:
    diffs = []
    for field in ("method", "path", "content_type", "auth_type", "body_size"):
        if req_a.get(field) != req_b.get(field):
            diffs.append({"field": field, "a": req_a.get(field), "b": req_b.get(field)})
    return {"diffs": diffs, "identical": len(diffs) == 0, "diff_count": len(diffs)}
