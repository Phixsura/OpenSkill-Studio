"""App Consent Manager — track user consent for data processing.

Manages GDPR/privacy consent records:
- Record user consent per purpose (analytics, marketing, etc.)
- Track consent grants and withdrawals with timestamps
- Check active consent status
- Per-installation scoped consent
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ConsentRecord:
    """A consent grant or withdrawal."""

    user_id: str
    purpose: str
    granted: bool
    timestamp: float = field(default_factory=time.time)
    source: str = ""  # e.g. "signup_form", "settings_page", "api"


class AppConsentManager:
    """Track user consent for data processing."""

    def __init__(self) -> None:
        # (installation_id, user_id, purpose) → list[ConsentRecord]
        self._records: dict[tuple[str, str, str], list[ConsentRecord]] = {}

    def grant_consent(
        self,
        installation_id: str,
        user_id: str,
        purpose: str,
        source: str = "",
        now: float | None = None,
    ) -> ConsentRecord:
        """Record a consent grant."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not user_id:
            raise ValueError("user_id is required")
        if not purpose:
            raise ValueError("purpose is required")

        record = ConsentRecord(
            user_id=user_id, purpose=purpose,
            granted=True, timestamp=now or time.time(), source=source,
        )
        key = (installation_id, user_id, purpose)
        self._records.setdefault(key, []).append(record)
        return record

    def withdraw_consent(
        self,
        installation_id: str,
        user_id: str,
        purpose: str,
        source: str = "",
        now: float | None = None,
    ) -> ConsentRecord:
        """Record a consent withdrawal."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not user_id:
            raise ValueError("user_id is required")

        record = ConsentRecord(
            user_id=user_id, purpose=purpose,
            granted=False, timestamp=now or time.time(), source=source,
        )
        key = (installation_id, user_id, purpose)
        self._records.setdefault(key, []).append(record)
        return record

    def has_consent(self, installation_id: str, user_id: str, purpose: str) -> bool:
        """Check if user has active consent for a purpose."""
        key = (installation_id, user_id, purpose)
        records = self._records.get(key, [])
        if not records:
            return False
        return records[-1].granted

    def get_user_consents(self, installation_id: str, user_id: str) -> dict[str, bool]:
        """Get all consent statuses for a user."""
        result: dict[str, bool] = {}
        for (inst, uid, purpose), records in self._records.items():
            if inst == installation_id and uid == user_id and records:
                result[purpose] = records[-1].granted
        return result

    def get_consent_history(
        self, installation_id: str, user_id: str, purpose: str
    ) -> list[ConsentRecord]:
        """Get consent history for a user/purpose, newest first."""
        key = (installation_id, user_id, purpose)
        return list(reversed(self._records.get(key, [])))

    def get_consented_users(self, installation_id: str, purpose: str) -> list[str]:
        """Get all users who currently consent to a purpose."""
        users = []
        for (inst, uid, p), records in self._records.items():
            if inst == installation_id and p == purpose and records and records[-1].granted:
                users.append(uid)
        return sorted(users)
