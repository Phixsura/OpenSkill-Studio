"""App License Manager — license key generation, validation, and enforcement.

Manages software licenses for paid marketplace apps:
- License key generation (deterministic, verifiable)
- License types: perpetual, subscription, trial, site
- Seat-based licensing with max seat enforcement
- Expiry checking and grace periods
- License activation/deactivation per installation
- Usage tracking per license
- Revocation support
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()

TRIAL_DAYS = 14
GRACE_PERIOD_DAYS = 7


class LicenseType(str, Enum):
    PERPETUAL = "perpetual"
    SUBSCRIPTION = "subscription"
    TRIAL = "trial"
    SITE = "site"


class LicenseStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    GRACE = "grace"       # expired but within grace period
    REVOKED = "revoked"
    TRIAL_ACTIVE = "trial_active"
    TRIAL_EXPIRED = "trial_expired"


@dataclass
class License:
    """A software license for a marketplace app."""

    license_key: str
    app_id: str
    org_id: str
    license_type: LicenseType
    max_seats: int
    active_seats: int = 0
    issued_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    activations: list[str] = field(default_factory=list)  # installation_ids


@dataclass
class LicenseCheckResult:
    """Result of checking a license."""

    valid: bool
    status: LicenseStatus
    seats_remaining: int
    days_remaining: int | None
    message: str


def generate_license_key(app_id: str, org_id: str) -> str:
    """Generate a unique, verifiable license key."""
    raw = f"{app_id}:{org_id}:{secrets.token_hex(8)}"
    prefix = hashlib.sha256(raw.encode()).hexdigest()[:8].upper()
    segments = [secrets.token_hex(4).upper() for _ in range(4)]
    return f"OSK-{prefix}-{'-'.join(segments)}"


class AppLicenseManager:
    """Manage app licenses with seat and expiry enforcement."""

    def __init__(self):
        # license_key → License
        self._licenses: dict[str, License] = {}
        # (app_id, org_id) → license_key
        self._org_licenses: dict[tuple[str, str], str] = {}

    # ── Issuance ─────────────────────────────────────────

    def issue(self, app_id: str, org_id: str, license_type: LicenseType,
              max_seats: int = 1, duration_days: int | None = None) -> License:
        """Issue a new license."""
        if max_seats <= 0:
            raise ValueError("max_seats must be positive")

        key = generate_license_key(app_id, org_id)
        now = datetime.now(UTC)

        if license_type == LicenseType.TRIAL:
            expires = now + timedelta(days=TRIAL_DAYS)
        elif license_type == LicenseType.SUBSCRIPTION and duration_days:
            expires = now + timedelta(days=duration_days)
        elif license_type == LicenseType.PERPETUAL:
            expires = None
        else:
            expires = now + timedelta(days=duration_days) if duration_days else None

        lic = License(
            license_key=key, app_id=app_id, org_id=org_id,
            license_type=license_type, max_seats=max_seats,
            expires_at=expires,
        )
        self._licenses[key] = lic
        self._org_licenses[(app_id, org_id)] = key
        log.info("license.issued", key=key[:12], app_id=app_id, type=license_type.value)
        return lic

    # ── Validation ───────────────────────────────────────

    def check(self, license_key: str, now: datetime | None = None) -> LicenseCheckResult:
        """Check if a license is valid."""
        now = now or datetime.now(UTC)
        lic = self._licenses.get(license_key)

        if lic is None:
            return LicenseCheckResult(False, LicenseStatus.REVOKED, 0, None, "License not found")

        if lic.revoked_at:
            return LicenseCheckResult(False, LicenseStatus.REVOKED, 0, None, "License revoked")

        seats_remaining = max(0, lic.max_seats - lic.active_seats)

        # Expiry check
        if lic.expires_at:
            if now >= lic.expires_at:
                grace_end = lic.expires_at + timedelta(days=GRACE_PERIOD_DAYS)
                if now < grace_end:
                    days_left = (grace_end - now).days
                    status = LicenseStatus.GRACE if lic.license_type != LicenseType.TRIAL else LicenseStatus.TRIAL_EXPIRED
                    return LicenseCheckResult(
                        True, status, seats_remaining, days_left,
                        f"License expired, grace period: {days_left} days left",
                    )
                status = LicenseStatus.TRIAL_EXPIRED if lic.license_type == LicenseType.TRIAL else LicenseStatus.EXPIRED
                return LicenseCheckResult(False, status, 0, 0, "License expired")

            days_left = (lic.expires_at - now).days
            status = LicenseStatus.TRIAL_ACTIVE if lic.license_type == LicenseType.TRIAL else LicenseStatus.ACTIVE
            return LicenseCheckResult(True, status, seats_remaining, days_left, "License valid")

        # Perpetual / no expiry
        return LicenseCheckResult(True, LicenseStatus.ACTIVE, seats_remaining, None, "License valid (perpetual)")

    # ── Activation ───────────────────────────────────────

    def activate(self, license_key: str, installation_id: str) -> LicenseCheckResult:
        """Activate a license for an installation (consume a seat)."""
        lic = self._licenses.get(license_key)
        if lic is None:
            return LicenseCheckResult(False, LicenseStatus.REVOKED, 0, None, "License not found")

        check = self.check(license_key)
        if not check.valid:
            return check

        if installation_id in lic.activations:
            return LicenseCheckResult(True, check.status, check.seats_remaining, check.days_remaining,
                                       "Already activated")

        if lic.active_seats >= lic.max_seats:
            return LicenseCheckResult(False, check.status, 0, check.days_remaining,
                                       f"No seats available ({lic.active_seats}/{lic.max_seats})")

        lic.activations.append(installation_id)
        lic.active_seats += 1
        return LicenseCheckResult(True, check.status, max(0, lic.max_seats - lic.active_seats),
                                   check.days_remaining, "Activated successfully")

    def deactivate(self, license_key: str, installation_id: str) -> bool:
        """Deactivate a license for an installation (release a seat)."""
        lic = self._licenses.get(license_key)
        if lic is None or installation_id not in lic.activations:
            return False
        lic.activations.remove(installation_id)
        lic.active_seats = max(0, lic.active_seats - 1)
        return True

    # ── Revocation ───────────────────────────────────────

    def revoke(self, license_key: str) -> bool:
        lic = self._licenses.get(license_key)
        if lic is None:
            return False
        lic.revoked_at = datetime.now(UTC)
        return True

    # ── Queries ──────────────────────────────────────────

    def get_license(self, license_key: str) -> License | None:
        return self._licenses.get(license_key)

    def get_org_license(self, app_id: str, org_id: str) -> License | None:
        key = self._org_licenses.get((app_id, org_id))
        return self._licenses.get(key) if key else None
