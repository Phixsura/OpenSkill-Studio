"""Fleet Ingress TLS v9 — track TLS termination at ingress layer."""
from __future__ import annotations
def fleet_ingress_tls_v9(ingresses: list[dict]) -> dict:
    tls_enabled = [i for i in ingresses if i.get("tls")]
    hsts = [i for i in ingresses if i.get("hsts")]
    redirect = [i for i in ingresses if i.get("http_redirect")]
    return {"ingresses": len(ingresses), "tls_enabled": len(tls_enabled), "hsts": len(hsts),
            "http_redirect": len(redirect), "healthy": len(tls_enabled) == len(ingresses)}
