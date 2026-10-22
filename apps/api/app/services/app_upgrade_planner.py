"""Upgrade planner — plan batch upgrades for all installations of an app."""


def plan_batch_upgrade(installations: list[dict], *, target_version: str, new_permissions: list[str]) -> dict:
    auto = [i for i in installations if not new_permissions and i.get("auto_upgrade", True)]
    manual = [i for i in installations if i not in auto]
    return {
        "target_version": target_version,
        "total": len(installations),
        "auto_upgrade": len(auto),
        "manual_upgrade": len(manual),
        "needs_consent": bool(new_permissions),
        "new_permissions": new_permissions,
        "auto_ids": [i.get("id") for i in auto],
        "manual_ids": [i.get("id") for i in manual],
    }
