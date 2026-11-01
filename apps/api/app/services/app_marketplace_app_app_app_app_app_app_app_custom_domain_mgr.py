"""Custom domain manager — manage custom domains for apps."""
from __future__ import annotations
import re
from urllib.parse import urlparse

DOMAIN_RE = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$")
_domains: dict[str, dict] = {}


def add_domain(app_id: str, domain: str) -> dict:
    d = domain.lower().strip()
    if not DOMAIN_RE.match(d):
        return {"added": False, "error": "invalid_domain"}
    if d in _domains:
        return {"added": False, "error": "already_registered"}
    _domains[d] = {"app_id": app_id, "domain": d, "verified": False,
                    "ssl": False, "dns_record": f"CNAME {d} -> apps.openskill.io"}
    return {"added": True, "domain": d, "dns_record": _domains[d]["dns_record"]}


def verify_domain(domain: str) -> dict:
    d = domain.lower().strip()
    if d not in _domains:
        return {"verified": False, "error": "not_found"}
    _domains[d]["verified"] = True
    _domains[d]["ssl"] = True
    return {"verified": True, "domain": d, "ssl": True}


def list_domains(app_id: str) -> list[dict]:
    return [v for v in _domains.values() if v["app_id"] == app_id]


def remove_domain(domain: str) -> dict:
    d = domain.lower().strip()
    if d in _domains:
        del _domains[d]
        return {"removed": True}
    return {"removed": False, "error": "not_found"}


def clear_domains() -> None:
    _domains.clear()
