"""Developer changelog aggregator — combine changelogs across all apps."""

def aggregate_changelogs(*, apps_changelogs: dict[str, list[dict]]) -> list[dict]:
    all_entries = []
    for app_name, entries in apps_changelogs.items():
        for e in entries:
            all_entries.append({**e, "app_name": app_name})
    return sorted(all_entries, key=lambda e: e.get("released_at", ""), reverse=True)

def group_by_month(*, entries: list[dict]) -> list[dict]:
    groups: dict[str, list] = {}
    for e in entries:
        month = e.get("released_at", "")[:7]
        groups.setdefault(month, []).append(e)
    return [{"month": m, "entries": ents, "count": len(ents)} for m, ents in sorted(groups.items(), reverse=True)]
