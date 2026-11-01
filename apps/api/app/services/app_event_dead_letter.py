"""Event dead letter queue — store events that failed all delivery attempts."""

from collections import defaultdict
from datetime import UTC, datetime

_dead_letters: dict[str, list[dict]] = defaultdict(list)


def add_dead_letter(*, app_id: str, event_id: str, event_type: str, url: str, error: str, attempts: int) -> dict:
    entry = {"event_id": event_id, "event_type": event_type, "url": url,
             "error": error, "attempts": attempts, "dead_at": datetime.now(UTC).isoformat()}
    _dead_letters[app_id].append(entry)
    return entry


def get_dead_letters(app_id: str, *, limit: int = 50) -> list[dict]:
    return _dead_letters.get(app_id, [])[-limit:]


def retry_dead_letter(app_id: str, event_id: str) -> dict | None:
    letters = _dead_letters.get(app_id, [])
    for i, dl in enumerate(letters):
        if dl["event_id"] == event_id:
            letters.pop(i)
            return dl
    return None


def get_dead_letter_count(app_id: str) -> int:
    return len(_dead_letters.get(app_id, []))


def purge_dead_letters(app_id: str) -> int:
    count = len(_dead_letters.pop(app_id, []))
    return count
