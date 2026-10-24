"""Event deduplicator — prevent duplicate event processing."""

from collections import OrderedDict

_seen: OrderedDict[str, bool] = OrderedDict()
MAX_SEEN = 10000


def is_duplicate(event_id: str) -> bool:
    """Check if we've already processed this event."""
    if event_id in _seen:
        return True
    _seen[event_id] = True
    while len(_seen) > MAX_SEEN:
        _seen.popitem(last=False)
    return False


def mark_processed(event_id: str) -> None:
    """Explicitly mark an event as processed."""
    _seen[event_id] = True
    while len(_seen) > MAX_SEEN:
        _seen.popitem(last=False)


def clear() -> int:
    count = len(_seen)
    _seen.clear()
    return count
