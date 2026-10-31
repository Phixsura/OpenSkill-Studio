"""Platform ingress controller — manage ingress rules and TLS termination."""
from __future__ import annotations


class IngressController:
    def __init__(self):
        self._rules: list[dict] = []
        self._certs: dict[str, dict] = {}

    def add_rule(self, host: str, path: str, backend: str, tls: bool = True) -> dict:
        rule = {"host": host, "path": path, "backend": backend, "tls": tls}
        self._rules.append(rule)
        return {"added": True, "total_rules": len(self._rules)}

    def add_cert(self, domain: str, issuer: str, expires_days: int) -> dict:
        self._certs[domain] = {"domain": domain, "issuer": issuer,
                                "expires_days": expires_days,
                                "valid": expires_days > 0}
        return self._certs[domain]

    def match(self, host: str, path: str) -> dict:
        for rule in self._rules:
            if rule["host"] == host and path.startswith(rule["path"]):
                return {"matched": True, "backend": rule["backend"], "tls": rule["tls"]}
        return {"matched": False}

    def expiring_certs(self, within_days: int = 30) -> list[dict]:
        return [c for c in self._certs.values() if 0 < c["expires_days"] <= within_days]

    def stats(self) -> dict:
        tls_count = sum(1 for r in self._rules if r["tls"])
        return {"rules": len(self._rules), "tls_enabled": tls_count,
                "certs": len(self._certs)}
