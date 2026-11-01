"""Network policy — ingress/egress firewall rule builder."""

import html
from urllib.parse import urlparse


PROTOCOLS = {"tcp", "udp", "icmp"}


def build_network_policy(*, rules: list[dict]) -> dict:
    ingress = []
    egress = []
    errors = []
    for r in rules:
        direction = r.get("direction", "ingress")
        proto = r.get("protocol", "tcp")
        if proto not in PROTOCOLS:
            errors.append(f"Invalid protocol: {proto}")
            continue
        port = r.get("port")
        if port is not None and not (1 <= port <= 65535):
            errors.append(f"Invalid port: {port}")
            continue
        entry = {
            "source": html.escape(r.get("source", "0.0.0.0/0")),
            "protocol": proto,
            "port": port,
            "action": r.get("action", "allow"),
            "description": html.escape(r.get("description", "")),
        }
        if direction == "ingress":
            ingress.append(entry)
        else:
            egress.append(entry)
    return {"ingress": ingress, "egress": egress,
            "ingress_count": len(ingress), "egress_count": len(egress),
            "errors": errors, "valid": len(errors) == 0}
