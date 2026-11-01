"""Webhook event catalog — complete reference of all platform events."""

EVENT_CATALOG = {
    "submission": {
        "description": "Events related to project submissions",
        "events": {
            "submission.completed": "A learner submitted their work",
            "submission.graded": "A submission received an evaluation score",
        },
    },
    "cohort": {
        "description": "Events related to cohort membership",
        "events": {
            "cohort.member_added": "A user was added to a cohort",
            "cohort.member_removed": "A user was removed from a cohort",
        },
    },
    "project": {
        "description": "Events related to project lifecycle",
        "events": {"project.published": "A project was published"},
    },
    "app": {
        "description": "Events related to app lifecycle",
        "events": {
            "app.installed": "An app was installed in an organization",
            "app.uninstalled": "An app was uninstalled from an organization",
        },
    },
}


def get_catalog() -> dict:
    return EVENT_CATALOG


def search_catalog(query: str) -> list[dict]:
    q = query.lower()
    results = []
    for cat, info in EVENT_CATALOG.items():
        for event, desc in info["events"].items():
            if q in event.lower() or q in desc.lower():
                results.append({"event": event, "description": desc, "category": cat})
    return results


def get_all_events() -> list[str]:
    return sorted(e for info in EVENT_CATALOG.values() for e in info["events"])
