"""Sandbox Network Policy — fine-grained network access control for sandboxed extensions.

Manages allowlist/denylist rules for outbound connections, DNS resolution
control, bandwidth limits, and connection auditing per extension sandbox.
"""
from __future__ import annotations
import ipaddress
import re
import secrets
from dataclasses import dataclass, field
from enum import Enum


class RuleAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class Protocol(str, Enum):
    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"
    UDP = "udp"


@dataclass
class NetworkRule:
    rule_id: str
    action: RuleAction
    host_pattern: str  # glob pattern or exact host
    ports: list[int] = field(default_factory=list)  # empty = all ports
    protocols: list[Protocol] = field(default_factory=list)
    priority: int = 0  # higher = evaluated first


@dataclass
class NetworkPolicy:
    extension_id: str
    default_action: RuleAction = RuleAction.DENY  # deny by default
    rules: list[NetworkRule] = field(default_factory=list)
    bandwidth_limit_kbps: int = 1024  # 1 Mbps default
    max_connections: int = 10
    dns_allowed: bool = True
    connection_log: list[dict] = field(default_factory=list)


PRIVATE_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
]


class SandboxNetworkService:
    """Manages network policies for extension sandboxes."""

    def __init__(self):
        self._policies: dict[str, NetworkPolicy] = {}

    def create_policy(self, extension_id: str,
                      default_action: RuleAction = RuleAction.DENY,
                      bandwidth_limit_kbps: int = 1024,
                      max_connections: int = 10) -> NetworkPolicy:
        policy = NetworkPolicy(
            extension_id=extension_id, default_action=default_action,
            bandwidth_limit_kbps=max(1, min(bandwidth_limit_kbps, 10240)),
            max_connections=max(1, min(max_connections, 100)),
        )
        self._policies[extension_id] = policy
        return policy

    def add_rule(self, extension_id: str, action: RuleAction,
                 host_pattern: str, ports: list[int] | None = None,
                 protocols: list[Protocol] | None = None,
                 priority: int = 0) -> NetworkRule:
        policy = self._policies.get(extension_id)
        if not policy:
            raise ValueError("No policy for extension")
        # Block private IP ranges in allow rules
        if action == RuleAction.ALLOW:
            try:
                ip = ipaddress.ip_address(host_pattern)
                if any(ip in net for net in PRIVATE_RANGES):
                    raise ValueError(f"Cannot allow private IP: {host_pattern}")
            except ValueError as e:
                if "private IP" in str(e):
                    raise
                # Not an IP, it's a hostname pattern — ok

        rule = NetworkRule(
            rule_id=f"nr_{secrets.token_urlsafe(8)}",
            action=action, host_pattern=host_pattern,
            ports=ports or [], protocols=protocols or [],
            priority=priority,
        )
        policy.rules.append(rule)
        policy.rules.sort(key=lambda r: r.priority, reverse=True)
        return rule

    def check_connection(self, extension_id: str, host: str,
                         port: int, protocol: Protocol) -> dict:
        policy = self._policies.get(extension_id)
        if not policy:
            return {"allowed": False, "reason": "No policy configured"}

        # Block private IPs regardless of rules
        try:
            ip = ipaddress.ip_address(host)
            if any(ip in net for net in PRIVATE_RANGES):
                return {"allowed": False, "reason": "Private IP blocked"}
        except ValueError:
            pass  # hostname, not IP

        # Evaluate rules by priority
        for rule in policy.rules:
            if self._matches(rule, host, port, protocol):
                allowed = rule.action == RuleAction.ALLOW
                result = {"allowed": allowed, "rule_id": rule.rule_id,
                          "reason": f"Matched rule: {rule.action.value}"}
                policy.connection_log.append({
                    "host": host, "port": port, "allowed": allowed,
                })
                return result

        allowed = policy.default_action == RuleAction.ALLOW
        policy.connection_log.append({"host": host, "port": port, "allowed": allowed})
        return {"allowed": allowed, "reason": f"Default: {policy.default_action.value}"}

    def _matches(self, rule: NetworkRule, host: str, port: int,
                 protocol: Protocol) -> bool:
        # Check host pattern
        pattern = rule.host_pattern.replace(".", r"\.").replace("*", ".*")
        if not re.fullmatch(pattern, host):
            return False
        if rule.ports and port not in rule.ports:
            return False
        if rule.protocols and protocol not in rule.protocols:
            return False
        return True

    def get_audit_log(self, extension_id: str) -> list[dict]:
        policy = self._policies.get(extension_id)
        return policy.connection_log if policy else []
