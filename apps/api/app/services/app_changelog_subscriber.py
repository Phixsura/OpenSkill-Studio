"""Changelog subscriber — manage users subscribed to app changelog updates."""

from collections import defaultdict

_subscriptions: dict[str, set[str]] = defaultdict(set)  # app_id -> set of user_ids


def subscribe(app_id: str, user_id: str) -> bool:
    if user_id in _subscriptions[app_id]:
        return False
    _subscriptions[app_id].add(user_id)
    return True


def unsubscribe(app_id: str, user_id: str) -> bool:
    if user_id not in _subscriptions.get(app_id, set()):
        return False
    _subscriptions[app_id].discard(user_id)
    return True


def get_subscribers(app_id: str) -> list[str]:
    return sorted(_subscriptions.get(app_id, set()))


def is_subscribed(app_id: str, user_id: str) -> bool:
    return user_id in _subscriptions.get(app_id, set())


def get_subscriber_count(app_id: str) -> int:
    return len(_subscriptions.get(app_id, set()))
