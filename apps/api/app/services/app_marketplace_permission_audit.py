"""Permission audit — track and review permission grants for installed apps."""

from datetime import datetime, timezone


def audit_permissions(*, installation: dict, granted_scopes: list[str],
                        used_scopes: list[str]) -> dict:
    granted = set(granted_scopes)
    used = set(used_scopes)
    unused = granted - used
    return {
        "installation_id": installation.get("id"),
        "granted_count": len(granted), "used_count": len(used),
        "unused_scopes": sorted(unused), "over_privileged": len(unused) > len(used),
        "recommendation": "Consider revoking unused permissions" if unused else "Permissions look good",
    }


def build_permission_diff(*, old_scopes: list[str], new_scopes: list[str]) -> dict:
    old, new = set(old_scopes), set(new_scopes)
    return {
        "added": sorted(new - old), "removed": sorted(old - new),
        "unchanged": sorted(old & new), "has_changes": old != new,
    }


def check_sensitive_scopes(*, scopes: list[str]) -> dict:
    sensitive = {"admin", "delete", "billing", "user_management", "org_settings"}
    found = [s for s in scopes if s in sensitive]
    return {"has_sensitive": len(found) > 0, "sensitive_scopes": found,
            "requires_admin_approval": len(found) > 0}
