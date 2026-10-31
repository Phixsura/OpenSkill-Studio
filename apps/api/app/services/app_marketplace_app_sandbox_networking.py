"""Sandbox networking — egress rules and DNS resolution for sandboxed apps."""

import ipaddress
import re

BLOCKED_PORTS = {22, 25, 53, 3306, 5432, 6379, 27017}
ALLOWED_SCHEMES = {"https"}


def validate_egress_rule(*, destination: str, port: int, protocol: str = "tcp") -> dict:
    errors = []
    if port in BLOCKED_PORTS:
        errors.append(f"Port {port} is blocked for security")
    if port < 1 or port > 65535:
        errors.append("Port must be 1-65535")
    try:
        ip = ipaddress.ip_address(destination)
        if ip.is_private or ip.is_loopback or ip.is_reserved:
            errors.append("Cannot connect to private/loopback/reserved IPs")
    except ValueError:
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?$', destination):
            errors.append("Invalid hostname")
    return {"valid": len(errors) == 0, "errors": errors}


def build_network_policy(*, allowed_hosts: list[str], max_connections: int = 50,
                            bandwidth_limit_mbps: int = 10) -> dict:
    return {
        "allowed_hosts": allowed_hosts, "blocked_ports": sorted(BLOCKED_PORTS),
        "max_connections": max_connections, "bandwidth_limit_mbps": bandwidth_limit_mbps,
        "allow_dns": True, "allow_private_networks": False,
    }
