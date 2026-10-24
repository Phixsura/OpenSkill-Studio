"""Fleet gateway auth — track API gateway authentication methods."""
from __future__ import annotations
def fleet_gw_auth(endpoints: list[dict]) -> dict:
    by_method: dict[str, int] = {}
    for e in endpoints:
        m = e.get("auth_method", "none")
        by_method[m] = by_method.get(m, 0) + 1
    no_auth = by_method.get("none", 0)
    return {"total": len(endpoints), "by_method": by_method, "no_auth": no_auth,
            "secure": no_auth == 0}
