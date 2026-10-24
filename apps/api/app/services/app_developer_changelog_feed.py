"""Developer changelog feed — aggregate changelogs across all apps."""


def build_developer_feed(apps_changelogs: list[dict]) -> list[dict]:
    """Merge changelogs from multiple apps into one feed, sorted by date."""
    feed = []
    for app_cl in apps_changelogs:
        app_name = app_cl.get("app_name", "Unknown")
        for entry in app_cl.get("entries", []):
            feed.append({**entry, "app_name": app_name})
    return sorted(feed, key=lambda e: e.get("date", ""), reverse=True)


def filter_breaking_only(feed: list[dict]) -> list[dict]:
    return [e for e in feed if e.get("breaking")]
