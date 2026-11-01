"""Event router — route events to matching subscriptions."""


def route_event(*, event_type: str, org_id: str, subscriptions: list[dict]) -> list[dict]:
    """Find subscriptions matching an event type + org."""
    matched = []
    for sub in subscriptions:
        if sub.get("event_type") != event_type:
            continue
        if not sub.get("enabled", True):
            continue
        # Org scope: subscription's installation must belong to this org
        sub_org = sub.get("org_id")
        if not sub_org or not org_id or sub_org != org_id:
            continue
        matched.append(sub)
    return matched


def group_by_installation(subscriptions: list[dict]) -> dict[str, list[dict]]:
    """Group matched subscriptions by installation_id."""
    groups: dict[str, list[dict]] = {}
    for sub in subscriptions:
        iid = sub.get("installation_id", "")
        if iid not in groups:
            groups[iid] = []
        groups[iid].append(sub)
    return groups
