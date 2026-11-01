"""Changelog notifier — notify installations when a new version is available."""


def build_upgrade_notification(*, app_name: str, from_version: str, to_version: str,
                               changelog: str = "", breaking: bool = False) -> dict:
    urgency = "high" if breaking else "normal"
    title = f"{'⚠️ Breaking update' if breaking else '🆕 Update available'}: {app_name} v{to_version}"
    return {
        "title": title,
        "body": f"Upgrade from v{from_version} to v{to_version}.{' ' + changelog if changelog else ''}",
        "urgency": urgency,
        "action_url": f"/apps/{app_name.lower().replace(' ', '-')}/upgrade",
        "breaking": breaking,
    }


def should_auto_upgrade(*, breaking: bool, org_auto_upgrade: bool = True) -> bool:
    return org_auto_upgrade and not breaking
