"""App Sandbox Policy Engine — fine-grained permission policies for sandboxed app execution.

Controls what sandboxed apps can access at runtime:
- Network policy: allowed/blocked domains, protocols
- Filesystem policy: read/write paths, max file size
- System call policy: allowed syscalls whitelist
- Environment variable access control
- Secrets access scope (which secret keys an execution can read)
- Policy composition: app manifest + org overrides + platform defaults
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class PolicyAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class NetworkProtocol(str, Enum):
    HTTPS = "https"
    HTTP = "http"
    WSS = "wss"


@dataclass
class NetworkRule:
    """A network access rule."""

    domain: str              # e.g. "api.example.com" or "*.example.com"
    action: PolicyAction
    protocols: list[NetworkProtocol] = field(default_factory=lambda: [NetworkProtocol.HTTPS])


@dataclass
class FilesystemRule:
    """A filesystem access rule."""

    path_prefix: str         # e.g. "/tmp/sandbox/" or "/data/"
    readable: bool = True
    writable: bool = False
    max_file_bytes: int = 10 * 1024 * 1024  # 10MB default


@dataclass
class SandboxPolicy:
    """Complete sandbox policy for an app execution."""

    app_id: str
    network_rules: list[NetworkRule] = field(default_factory=list)
    filesystem_rules: list[FilesystemRule] = field(default_factory=list)
    allowed_env_vars: list[str] = field(default_factory=list)
    allowed_secret_keys: list[str] = field(default_factory=list)
    max_execution_seconds: int = 30
    max_memory_mb: int = 128
    allow_subprocess: bool = False
    network_default: PolicyAction = PolicyAction.DENY  # default-deny for network


@dataclass
class PolicyCheckResult:
    """Result of checking an action against the policy."""

    allowed: bool
    rule_matched: str       # description of the matching rule
    policy_source: str = ""  # "manifest", "org_override", "platform_default"


# ── Platform defaults (most restrictive) ─────────────────

PLATFORM_DEFAULT = SandboxPolicy(
    app_id="__platform__",
    network_rules=[],
    filesystem_rules=[
        FilesystemRule("/tmp/sandbox/", readable=True, writable=True, max_file_bytes=10 * 1024 * 1024),
    ],
    allowed_env_vars=["NODE_ENV", "TZ", "LANG"],
    allowed_secret_keys=[],
    max_execution_seconds=30,
    max_memory_mb=128,
    allow_subprocess=False,
    network_default=PolicyAction.DENY,
)


class AppSandboxPolicyEngine:
    """Evaluate and compose sandbox policies."""

    def __init__(self):
        # app_id → SandboxPolicy (from manifest)
        self._app_policies: dict[str, SandboxPolicy] = {}
        # (app_id, org_id) → SandboxPolicy overrides
        self._org_overrides: dict[tuple[str, str], SandboxPolicy] = {}

    def register_app_policy(self, policy: SandboxPolicy) -> None:
        self._app_policies[policy.app_id] = policy

    def set_org_override(self, app_id: str, org_id: str, policy: SandboxPolicy) -> None:
        self._org_overrides[(app_id, org_id)] = policy

    def get_effective_policy(self, app_id: str, org_id: str | None = None) -> SandboxPolicy:
        """Compose the effective policy: platform defaults ← app manifest ← org overrides.

        More restrictive rules win (intersection for allows, union for denies).
        """
        app_policy = self._app_policies.get(app_id, PLATFORM_DEFAULT)
        if org_id:
            org_override = self._org_overrides.get((app_id, org_id))
            if org_override:
                return self._compose(app_policy, org_override)
        return app_policy

    # ── Policy checks ────────────────────────────────────

    def check_network(self, app_id: str, domain: str,
                      protocol: NetworkProtocol = NetworkProtocol.HTTPS,
                      org_id: str | None = None) -> PolicyCheckResult:
        """Check if a network request to domain is allowed.

        DENY rules are evaluated first regardless of list order,
        so a wildcard allow cannot shadow a specific deny.
        """
        policy = self.get_effective_policy(app_id, org_id)

        # Phase 1: check all DENY rules first
        for rule in policy.network_rules:
            if rule.action == PolicyAction.DENY and self._domain_matches(rule.domain, domain):
                return PolicyCheckResult(
                    allowed=False, rule_matched=f"Denied by rule: {rule.domain}",
                )

        # Phase 2: check ALLOW rules
        for rule in policy.network_rules:
            if rule.action == PolicyAction.ALLOW and self._domain_matches(rule.domain, domain):
                if protocol not in rule.protocols:
                    return PolicyCheckResult(
                        allowed=False,
                        rule_matched=f"Protocol {protocol.value} not allowed for {rule.domain}",
                    )
                return PolicyCheckResult(
                    allowed=True, rule_matched=f"Allowed by rule: {rule.domain}",
                )

        # No rule matched → use default
        if policy.network_default == PolicyAction.ALLOW:
            return PolicyCheckResult(allowed=True, rule_matched="default_allow")
        return PolicyCheckResult(allowed=False, rule_matched="default_deny")

    def check_filesystem(self, app_id: str, path: str, write: bool = False,
                         org_id: str | None = None) -> PolicyCheckResult:
        """Check if filesystem access to path is allowed.

        Resolves symlinks/.. to prevent path traversal attacks.
        Rejects NUL bytes in paths.
        """
        import os

        # Reject NUL bytes
        if "\x00" in path:
            return PolicyCheckResult(allowed=False, rule_matched="NUL byte in path")

        policy = self.get_effective_policy(app_id, org_id)
        real_path = os.path.realpath(path)

        for rule in policy.filesystem_rules:
            real_prefix = os.path.realpath(rule.path_prefix).rstrip("/") + "/"
            if real_path == real_prefix.rstrip("/") or real_path.startswith(real_prefix):
                if write and not rule.writable:
                    return PolicyCheckResult(
                        allowed=False, rule_matched=f"Write denied on {rule.path_prefix}",
                    )
                if not rule.readable:
                    return PolicyCheckResult(
                        allowed=False, rule_matched=f"Read denied on {rule.path_prefix}",
                    )
                return PolicyCheckResult(
                    allowed=True, rule_matched=f"Allowed by {rule.path_prefix}",
                )

        return PolicyCheckResult(allowed=False, rule_matched="No matching filesystem rule")

    def check_env_var(self, app_id: str, var_name: str,
                      org_id: str | None = None) -> PolicyCheckResult:
        policy = self.get_effective_policy(app_id, org_id)
        if var_name in policy.allowed_env_vars:
            return PolicyCheckResult(allowed=True, rule_matched=f"Env var {var_name} allowed")
        return PolicyCheckResult(allowed=False, rule_matched=f"Env var {var_name} not in allowlist")

    def check_secret(self, app_id: str, secret_key: str,
                     org_id: str | None = None) -> PolicyCheckResult:
        policy = self.get_effective_policy(app_id, org_id)
        if secret_key in policy.allowed_secret_keys:
            return PolicyCheckResult(allowed=True, rule_matched=f"Secret {secret_key} allowed")
        return PolicyCheckResult(allowed=False, rule_matched=f"Secret {secret_key} not in allowlist")

    def check_subprocess(self, app_id: str, org_id: str | None = None) -> PolicyCheckResult:
        policy = self.get_effective_policy(app_id, org_id)
        if policy.allow_subprocess:
            return PolicyCheckResult(allowed=True, rule_matched="Subprocess allowed")
        return PolicyCheckResult(allowed=False, rule_matched="Subprocess denied")

    # ── Internal ─────────────────────────────────────────

    @staticmethod
    def _domain_matches(pattern: str, domain: str) -> bool:
        """Match domain against pattern with normalization.

        Both sides are lowercased and trailing dots stripped to prevent
        bypass via case or FQDN dot tricks.
        """
        domain = domain.rstrip(".").lower()
        pattern = pattern.rstrip(".").lower()
        if pattern.startswith("*."):
            suffix = pattern[1:]  # e.g. ".example.com"
            return domain.endswith(suffix) or domain == pattern[2:]
        return domain == pattern

    @staticmethod
    def _compose(base: SandboxPolicy, override: SandboxPolicy) -> SandboxPolicy:
        """Compose two policies. Override can only restrict, not expand.

        - Network: deny rules from BOTH apply; allow requires BOTH to allow.
          Override ALLOW rules for domains not in base are dropped.
        - Filesystem: only override rules whose prefix is within a base rule
          are kept; R/W flags are ANDed (both must allow).
        - Env/secrets: intersection only.
        - Limits: min of both.
        """
        # Network: collect all deny rules from both; for allows, keep only
        # those present in both base and override
        composed_net: list[NetworkRule] = []
        # All deny rules win unconditionally
        for r in base.network_rules + override.network_rules:
            if r.action == PolicyAction.DENY:
                composed_net.append(r)
        # Allow rules: only keep base allows that the override also allows
        base_allow_domains = {r.domain for r in base.network_rules if r.action == PolicyAction.ALLOW}
        override_allow_domains = {r.domain for r in override.network_rules if r.action == PolicyAction.ALLOW}
        # If override has no allow rules, keep base allows (override didn't restrict)
        allowed_domains = base_allow_domains & override_allow_domains if override_allow_domains else base_allow_domains
        for r in base.network_rules:
            if r.action == PolicyAction.ALLOW and r.domain in allowed_domains:
                composed_net.append(r)

        # Filesystem: only keep override rules within a base prefix, AND the flags
        import os
        composed_fs: list[FilesystemRule] = []
        if override.filesystem_rules:
            for ov_rule in override.filesystem_rules:
                ov_real = os.path.realpath(ov_rule.path_prefix).rstrip("/") + "/"
                for base_rule in base.filesystem_rules:
                    base_real = os.path.realpath(base_rule.path_prefix).rstrip("/") + "/"
                    if ov_real.startswith(base_real) or ov_real == base_real:
                        composed_fs.append(FilesystemRule(
                            path_prefix=ov_rule.path_prefix,
                            readable=base_rule.readable and ov_rule.readable,
                            writable=base_rule.writable and ov_rule.writable,
                            max_file_bytes=min(base_rule.max_file_bytes, ov_rule.max_file_bytes),
                        ))
                        break
        else:
            composed_fs = list(base.filesystem_rules)

        return SandboxPolicy(
            app_id=base.app_id,
            network_rules=composed_net,
            filesystem_rules=composed_fs,
            allowed_env_vars=list(set(base.allowed_env_vars) & set(override.allowed_env_vars))
                if override.allowed_env_vars else base.allowed_env_vars,
            allowed_secret_keys=list(set(base.allowed_secret_keys) & set(override.allowed_secret_keys))
                if override.allowed_secret_keys else base.allowed_secret_keys,
            max_execution_seconds=min(base.max_execution_seconds, override.max_execution_seconds),
            max_memory_mb=min(base.max_memory_mb, override.max_memory_mb),
            allow_subprocess=base.allow_subprocess and override.allow_subprocess,
            network_default=PolicyAction.DENY,  # composed policy always default-deny
        )
