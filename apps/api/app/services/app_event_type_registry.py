"""Event type registry — metadata for all platform events."""

from dataclasses import dataclass
from app.services.event_dispatch import CANONICAL_EVENTS


@dataclass
class EventTypeInfo:
    name: str
    category: str
    description: str
    payload_fields: list[str]


EVENT_REGISTRY: dict[str, EventTypeInfo] = {}

def _register_events():
    descs = {
        "submission.completed": ("submission", "Fired when a submission is completed", ["submission_id", "project_id", "user_id"]),
        "submission.graded": ("submission", "Fired when a submission receives a grade", ["submission_id", "grade", "evaluator_id"]),
        "cohort.member_added": ("cohort", "A member was added to a cohort", ["cohort_id", "user_id"]),
        "cohort.member_removed": ("cohort", "A member was removed from a cohort", ["cohort_id", "user_id"]),
        "project.published": ("project", "A project was published", ["project_id"]),
        "app.installed": ("app", "An app was installed in an organization", ["app_id", "org_id", "installed_by"]),
        "app.uninstalled": ("app", "An app was uninstalled", ["app_id", "org_id"]),
    }
    for event in CANONICAL_EVENTS:
        cat = event.split(".")[0]
        info = descs.get(event)
        EVENT_REGISTRY[event] = EventTypeInfo(
            name=event, category=info[0] if info else cat,
            description=info[1] if info else f"Event: {event}",
            payload_fields=info[2] if info else [],
        )

_register_events()


def get_event_info(event_type: str) -> EventTypeInfo | None:
    return EVENT_REGISTRY.get(event_type)


def list_event_types() -> list[EventTypeInfo]:
    return sorted(EVENT_REGISTRY.values(), key=lambda e: e.name)


def get_events_by_category(category: str) -> list[EventTypeInfo]:
    return [e for e in EVENT_REGISTRY.values() if e.category == category]
