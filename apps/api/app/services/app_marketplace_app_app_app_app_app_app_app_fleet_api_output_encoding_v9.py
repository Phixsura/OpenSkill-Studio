"""Fleet API Output Encoding v9 — track response output encoding safety."""
from __future__ import annotations
def fleet_api_output_encoding_v9(endpoints: list[dict]) -> dict:
    encoded = [e for e in endpoints if e.get("output_encoded")]
    xss_safe = [e for e in endpoints if e.get("xss_safe")]
    total_responses = sum(e.get("responses_today", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "encoded": len(encoded), "xss_safe": len(xss_safe),
            "responses_today": total_responses, "healthy": len(encoded) == len(endpoints)}
