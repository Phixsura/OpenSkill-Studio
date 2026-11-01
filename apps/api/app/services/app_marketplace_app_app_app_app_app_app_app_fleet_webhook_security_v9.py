"""Fleet Webhook Security v9 — track webhook endpoint security measures."""
from __future__ import annotations
def fleet_webhook_security_v9(endpoints: list[dict]) -> dict:
    signed = [e for e in endpoints if e.get("hmac_signed")]
    tls = [e for e in endpoints if e.get("tls_only")]
    ip_filtered = [e for e in endpoints if e.get("ip_filter")]
    return {"endpoints": len(endpoints), "hmac_signed": len(signed), "tls_only": len(tls),
            "ip_filtered": len(ip_filtered), "healthy": len(signed) == len(endpoints)}
