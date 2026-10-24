"""Fleet API Response Header v9 — track security response headers."""
from __future__ import annotations
def fleet_api_response_header_v9(endpoints: list[dict]) -> dict:
    csp = [e for e in endpoints if e.get("csp")]
    hsts = [e for e in endpoints if e.get("hsts")]
    x_frame = [e for e in endpoints if e.get("x_frame_options")]
    return {"endpoints": len(endpoints), "csp": len(csp), "hsts": len(hsts),
            "x_frame_options": len(x_frame), "healthy": len(hsts) == len(endpoints)}
