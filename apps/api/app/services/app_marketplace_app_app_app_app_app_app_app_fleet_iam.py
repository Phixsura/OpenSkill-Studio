"""Fleet IAM — track identity and access management health."""
from __future__ import annotations
def fleet_iam_status(users: list[dict]) -> dict:
    with_mfa = [u for u in users if u.get("mfa_enabled", False)]
    unused_keys = [u for u in users if u.get("key_unused_days", 0) > 90]
    admin_users = [u for u in users if u.get("is_admin", False)]
    return {"total": len(users), "with_mfa": len(with_mfa), "unused_keys": len(unused_keys),
            "admins": len(admin_users), "secure": len(with_mfa) == len(users) and len(unused_keys) == 0}
