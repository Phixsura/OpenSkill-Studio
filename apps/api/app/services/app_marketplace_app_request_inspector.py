"""Request inspector — debug incoming API requests in detail."""

import hashlib
from datetime import datetime


def inspect_request(*, method: str, path: str, headers: dict,
                      body: str | None = None, query_params: dict | None = None) -> dict:
    content_length = len(body.encode()) if body else 0
    content_type = headers.get("content-type", headers.get("Content-Type", ""))
    auth_header = headers.get("authorization", headers.get("Authorization", ""))
    has_auth = bool(auth_header)
    auth_type = auth_header.split(" ")[0] if has_auth else None
    request_id = hashlib.sha256(f"{method}{path}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:12]
    return {
        "request_id": request_id,
        "method": method.upper(),
        "path": path,
        "query_params": query_params or {},
        "headers": {k: "***" if k.lower() in ("authorization", "cookie", "x-api-key") else v
                     for k, v in headers.items()},
        "body_size_bytes": content_length,
        "content_type": content_type,
        "has_auth": has_auth,
        "auth_type": auth_type,
        "timestamp": datetime.utcnow().isoformat(),
    }


def compare_requests(*, req_a: dict, req_b: dict) -> dict:
    diffs = []
    for key in set(list(req_a.keys()) + list(req_b.keys())):
        if key in ("request_id", "timestamp"):
            continue
        va = req_a.get(key)
        vb = req_b.get(key)
        if va != vb:
            diffs.append({"field": key, "a": va, "b": vb})
    return {"diffs": diffs, "diff_count": len(diffs), "identical": len(diffs) == 0}
