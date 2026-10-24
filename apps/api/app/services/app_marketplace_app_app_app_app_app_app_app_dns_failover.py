"""DNS failover controller — automatic DNS failover between regions."""
from __future__ import annotations


class DnsFailoverController:
    def __init__(self):
        self._records: dict[str, dict] = {}

    def register(self, domain: str, primary: str, secondary: str,
                 health_check_path: str = "/health") -> dict:
        self._records[domain] = {"domain": domain, "primary": primary,
                                  "secondary": secondary, "active": "primary",
                                  "health_check": health_check_path,
                                  "failover_count": 0}
        return self._records[domain]

    def failover(self, domain: str) -> dict:
        r = self._records[domain]
        if r["active"] == "primary":
            r["active"] = "secondary"
        r["failover_count"] += 1
        return {"domain": domain, "active": r["active"],
                "resolved_to": r[r["active"]], "failover_count": r["failover_count"]}

    def failback(self, domain: str) -> dict:
        r = self._records[domain]
        r["active"] = "primary"
        return {"domain": domain, "active": "primary", "resolved_to": r["primary"]}

    def resolve(self, domain: str) -> dict:
        r = self._records.get(domain)
        if not r:
            return {"domain": domain, "resolved": False}
        return {"domain": domain, "resolved": True,
                "ip": r[r["active"]], "active_region": r["active"]}

    def status(self) -> dict:
        failed_over = sum(1 for r in self._records.values() if r["active"] != "primary")
        return {"total_domains": len(self._records), "failed_over": failed_over}
