"""Permission Audit Engine — analyze extension permissions for least-privilege.

Detects:
- Over-permissioned extensions (requested but never used)
- Permission escalation between versions
- Dangerous permission combinations
- Unused permissions over time
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


DANGEROUS_COMBOS = [
    ({"write:data", "admin:settings"}, "Full data access + admin = potential data exfiltration"),
    ({"sandbox:execute", "webhook:manage"}, "Code execution + outbound webhooks = exfiltration risk"),
    ({"read:profile", "webhook:manage"}, "Profile read + webhooks = PII leak risk"),
]

PERMISSION_RISK = {
    "read:profile": 1, "read:data": 2, "read:analytics": 1,
    "write:profile": 3, "write:data": 4, "admin:settings": 5,
    "webhook:manage": 3, "sandbox:execute": 4, "connector:manage": 3,
    "marketplace:publish": 2,
}


@dataclass
class PermissionUsage:
    permission: str
    granted_at: float
    last_used: float = 0.0
    use_count: int = 0


@dataclass
class AuditResult:
    extension_id: str
    total_permissions: int = 0
    used_permissions: int = 0
    unused_permissions: list[str] = field(default_factory=list)
    dangerous_combos: list[str] = field(default_factory=list)
    risk_score: int = 0
    escalations: list[str] = field(default_factory=list)
    recommendation: str = ""


class PermAuditEngineService:
    def __init__(self):
        self._usage: dict[str, dict[str, PermissionUsage]] = {}  # ext_id -> {perm -> usage}
        self._version_perms: dict[str, dict[str, set[str]]] = {}  # ext_id -> {version -> perms}

    def grant(self, extension_id: str, permission: str) -> None:
        if extension_id not in self._usage:
            self._usage[extension_id] = {}
        self._usage[extension_id][permission] = PermissionUsage(
            permission=permission, granted_at=time.time())

    def record_use(self, extension_id: str, permission: str) -> bool:
        usage = self._usage.get(extension_id, {}).get(permission)
        if not usage:
            return False
        usage.last_used = time.time()
        usage.use_count += 1
        return True

    def record_version_permissions(self, extension_id: str, version: str,
                                   permissions: set[str]) -> None:
        if extension_id not in self._version_perms:
            self._version_perms[extension_id] = {}
        self._version_perms[extension_id][version] = permissions

    def audit(self, extension_id: str, stale_days: int = 30) -> AuditResult:
        usages = self._usage.get(extension_id, {})
        result = AuditResult(extension_id=extension_id)
        result.total_permissions = len(usages)

        now = time.time()
        cutoff = now - stale_days * 86400
        granted_perms = set(usages.keys())

        # Find unused/stale permissions
        for perm, usage in usages.items():
            if usage.use_count > 0:
                result.used_permissions += 1
                if usage.last_used < cutoff:
                    result.unused_permissions.append(f"{perm} (stale: not used in {stale_days}d)")
            else:
                result.unused_permissions.append(f"{perm} (never used)")

        # Check dangerous combinations
        for combo, reason in DANGEROUS_COMBOS:
            if combo.issubset(granted_perms):
                result.dangerous_combos.append(reason)

        # Calculate risk score
        result.risk_score = sum(PERMISSION_RISK.get(p, 1) for p in granted_perms)

        # Check version escalation
        versions = self._version_perms.get(extension_id, {})
        sorted_versions = sorted(versions.keys())
        for i in range(1, len(sorted_versions)):
            prev = versions[sorted_versions[i - 1]]
            curr = versions[sorted_versions[i]]
            new_perms = curr - prev
            if new_perms:
                for p in new_perms:
                    risk = PERMISSION_RISK.get(p, 1)
                    if risk >= 3:
                        result.escalations.append(
                            f"{sorted_versions[i]}: added {p} (risk {risk}/5)")

        # Recommendation
        unused_count = len(result.unused_permissions)
        if unused_count == 0 and not result.dangerous_combos:
            result.recommendation = "✅ Good: follows least-privilege principle"
        elif unused_count > 0 and not result.dangerous_combos:
            result.recommendation = f"⚠️ Remove {unused_count} unused permission(s)"
        elif result.dangerous_combos:
            result.recommendation = f"🔴 Review {len(result.dangerous_combos)} dangerous combination(s)"
        return result
