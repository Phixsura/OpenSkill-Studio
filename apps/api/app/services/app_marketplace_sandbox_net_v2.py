"""Sandbox networking v2 — DNS filtering and TLS inspection for sandboxed apps."""

import re

BLOCKED_DOMAINS = {"localhost", "127.0.0.1", "0.0.0.0", "metadata.google.internal", "169.254.169.254"}


def validate_outbound_request(*, hostname: str, port: int, protocol: str) -> dict:
    errors = []
    if hostname in BLOCKED_DOMAINS:
        errors.append(f"Blocked destination: {hostname}")
    if re.match(r'^10\.|^172\.(1[6-9]|2\d|3[01])\.|^192\.168\.', hostname):
        errors.append("Private IP ranges blocked")
    if protocol not in ("https", "wss"):
        errors.append(f"Only HTTPS/WSS allowed, got {protocol}")
    if port in (22, 25, 3306, 5432, 6379):
        errors.append(f"Port {port} blocked")
    return {"allowed": len(errors) == 0, "errors": errors}


def build_dns_allowlist(*, allowed_domains: list[str]) -> dict:
    return {"domains": allowed_domains, "count": len(allowed_domains),
            "mode": "allowlist" if allowed_domains else "open",
            "includes_wildcards": any("*" in d for d in allowed_domains)}


def compute_network_usage(*, requests: list[dict]) -> dict:
    total_bytes = sum(r.get("bytes", 0) for r in requests)
    unique_hosts = len(set(r.get("hostname", "") for r in requests))
    return {"total_requests": len(requests), "total_bytes": total_bytes,
            "unique_hosts": unique_hosts, "avg_bytes": round(total_bytes / max(len(requests), 1))}
