"""Developer agreement — track terms acceptance."""

from datetime import UTC, datetime

_agreements: dict[str, dict] = {}
CURRENT_TOS_VERSION = "2024-01-01"


def accept_agreement(developer_id: str, tos_version: str = CURRENT_TOS_VERSION) -> dict:
    entry = {"developer_id": developer_id, "tos_version": tos_version,
             "accepted_at": datetime.now(UTC).isoformat()}
    _agreements[developer_id] = entry
    return entry


def has_accepted(developer_id: str) -> bool:
    a = _agreements.get(developer_id)
    return a is not None and a.get("tos_version") == CURRENT_TOS_VERSION


def needs_reaccept(developer_id: str) -> bool:
    a = _agreements.get(developer_id)
    if not a:
        return True
    return a.get("tos_version") != CURRENT_TOS_VERSION
