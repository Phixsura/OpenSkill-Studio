"""Consumer IP Allowlist — IP-based access control with CIDR support."""
from __future__ import annotations

import ipaddress
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class AllowlistEntry:
    network: str
    label: str = ""
    added_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class IpAllowlist:
    """Manage per-consumer IP allowlists with CIDR matching."""

    _lists: dict[str, list[AllowlistEntry]] = field(default_factory=dict)
    _mode: dict[str, str] = field(default_factory=dict)  # allow or deny

    def set_mode(self, consumer_id: str, mode: str) -> dict:
        if mode not in ("allow", "deny"):
            raise ValueError("Mode must be 'allow' or 'deny'")
        self._mode[consumer_id] = mode
        return {"consumer_id": consumer_id, "mode": mode}

    def add_entry(self, consumer_id: str, network: str, label: str = "") -> dict:
        try:
            ipaddress.ip_network(network, strict=False)
        except ValueError as e:
            raise ValueError(f"Invalid network: {e}")
        entries = self._lists.setdefault(consumer_id, [])
        for existing in entries:
            if existing.network == network:
                raise ValueError(f"Network {network} already in list")
        entries.append(AllowlistEntry(network=network, label=label))
        logger.info("ip_entry_added", consumer_id=consumer_id, network=network)
        return {"consumer_id": consumer_id, "network": network, "total": len(entries)}

    def remove_entry(self, consumer_id: str, network: str) -> dict:
        entries = self._lists.get(consumer_id, [])
        before = len(entries)
        self._lists[consumer_id] = [e for e in entries if e.network != network]
        removed = before - len(self._lists[consumer_id])
        return {"removed": removed > 0}

    def check_access(self, consumer_id: str, ip: str) -> dict:
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return {"allowed": False, "reason": "invalid_ip"}
        entries = self._lists.get(consumer_id, [])
        mode = self._mode.get(consumer_id, "allow")
        if not entries:
            # No entries: allow mode = allow all, deny mode = allow all
            return {"allowed": True, "reason": "no_rules"}
        matched = False
        matched_network = None
        for entry in entries:
            net = ipaddress.ip_network(entry.network, strict=False)
            if addr in net:
                matched = True
                matched_network = entry.network
                break
        if mode == "allow":
            allowed = matched
            reason = "ip_allowed" if matched else "ip_not_in_allowlist"
        else:
            allowed = not matched
            reason = "ip_denied" if matched else "ip_not_in_denylist"
        result = {"allowed": allowed, "reason": reason, "ip": ip}
        if matched_network:
            result["matched_network"] = matched_network
        return result

    def list_entries(self, consumer_id: str) -> list[dict]:
        entries = self._lists.get(consumer_id, [])
        return [{"network": e.network, "label": e.label, "added_at": e.added_at}
                for e in entries]

    def get_stats(self, consumer_id: str) -> dict:
        entries = self._lists.get(consumer_id, [])
        mode = self._mode.get(consumer_id, "allow")
        total_ips = 0
        for e in entries:
            net = ipaddress.ip_network(e.network, strict=False)
            total_ips += net.num_addresses
        return {
            "consumer_id": consumer_id,
            "mode": mode,
            "entry_count": len(entries),
            "total_addresses": total_ips,
        }
