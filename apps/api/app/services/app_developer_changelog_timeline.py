"""Developer changelog timeline — time-ordered changelog across apps."""

def build_changelog_timeline(changelogs: list[dict], *, limit: int = 20) -> list[dict]:
    entries = []
    for cl in changelogs:
        app_name = cl.get("app_name", "")
        for entry in cl.get("entries", []):
            entries.append({**entry, "app_name": app_name})
    entries.sort(key=lambda e: e.get("date", ""), reverse=True)
    return entries[:limit]
