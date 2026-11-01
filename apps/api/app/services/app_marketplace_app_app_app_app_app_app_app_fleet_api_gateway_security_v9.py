"""Fleet API Gateway Security v9 — track gateway WAF and auth."""
from __future__ import annotations
def fleet_api_gateway_security_v9(gateways: list[dict]) -> dict:
    waf_enabled = [g for g in gateways if g.get("waf")]
    oauth_enabled = [g for g in gateways if g.get("oauth")]
    jwt_validation = [g for g in gateways if g.get("jwt_validation")]
    return {"gateways": len(gateways), "waf": len(waf_enabled), "oauth": len(oauth_enabled),
            "jwt_validation": len(jwt_validation), "healthy": len(waf_enabled) == len(gateways)}
