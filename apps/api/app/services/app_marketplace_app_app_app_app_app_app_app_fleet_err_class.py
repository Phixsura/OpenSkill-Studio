"""Fleet error classification — categorize errors by type."""
from __future__ import annotations
def fleet_error_classification(errors: list[dict]) -> dict:
    by_code: dict[int, int] = {}
    for e in errors:
        code = e.get("status_code", 500)
        by_code[code] = by_code.get(code, 0) + 1
    client_err = sum(v for k, v in by_code.items() if 400 <= k < 500)
    server_err = sum(v for k, v in by_code.items() if k >= 500)
    return {"total": len(errors), "client_errors": client_err, "server_errors": server_err, "by_code": by_code}
