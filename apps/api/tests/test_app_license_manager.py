"""Tests for App License Manager — issuance, validation, seats, expiry, revocation."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.app_license_manager import (
    AppLicenseManager,
    GRACE_PERIOD_DAYS,
    LicenseStatus,
    LicenseType,
    TRIAL_DAYS,
    generate_license_key,
)


class TestKeyGeneration:
    def test_format(self):
        key = generate_license_key("app-1", "org-1")
        assert key.startswith("OSK-")
        parts = key.split("-")
        assert len(parts) == 6  # OSK + prefix + 4 segments

    def test_unique(self):
        k1 = generate_license_key("app-1", "org-1")
        k2 = generate_license_key("app-1", "org-1")
        assert k1 != k2


class TestIssuance:
    def test_issue_perpetual(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.PERPETUAL, max_seats=5)
        assert lic.license_type == LicenseType.PERPETUAL
        assert lic.max_seats == 5
        assert lic.expires_at is None

    def test_issue_trial(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.TRIAL)
        assert lic.license_type == LicenseType.TRIAL
        assert lic.expires_at is not None
        delta = lic.expires_at - lic.issued_at
        assert TRIAL_DAYS - 1 <= delta.days <= TRIAL_DAYS

    def test_issue_subscription(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.SUBSCRIPTION, duration_days=365)
        assert lic.expires_at is not None

    def test_zero_seats_rejected(self):
        m = AppLicenseManager()
        with pytest.raises(ValueError, match="positive"):
            m.issue("app-1", "org-1", LicenseType.PERPETUAL, max_seats=0)

    def test_org_license_lookup(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.PERPETUAL)
        found = m.get_org_license("app-1", "org-1")
        assert found is not None
        assert found.license_key == lic.license_key


class TestValidation:
    def test_valid_perpetual(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.PERPETUAL)
        result = m.check(lic.license_key)
        assert result.valid is True
        assert result.status == LicenseStatus.ACTIVE
        assert result.days_remaining is None

    def test_valid_subscription(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.SUBSCRIPTION, duration_days=30)
        result = m.check(lic.license_key)
        assert result.valid is True
        assert result.days_remaining is not None
        assert result.days_remaining > 0

    def test_expired_subscription(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.SUBSCRIPTION, duration_days=30)
        future = datetime.now(UTC) + timedelta(days=31 + GRACE_PERIOD_DAYS + 1)
        result = m.check(lic.license_key, now=future)
        assert result.valid is False
        assert result.status == LicenseStatus.EXPIRED

    def test_grace_period(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.SUBSCRIPTION, duration_days=30)
        # Just after expiry, within grace
        grace_time = lic.expires_at + timedelta(days=1)
        result = m.check(lic.license_key, now=grace_time)
        assert result.valid is True
        assert result.status == LicenseStatus.GRACE

    def test_trial_active(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.TRIAL)
        result = m.check(lic.license_key)
        assert result.status == LicenseStatus.TRIAL_ACTIVE

    def test_trial_expired(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.TRIAL)
        future = datetime.now(UTC) + timedelta(days=TRIAL_DAYS + GRACE_PERIOD_DAYS + 1)
        result = m.check(lic.license_key, now=future)
        assert result.valid is False
        assert result.status == LicenseStatus.TRIAL_EXPIRED

    def test_unknown_key(self):
        m = AppLicenseManager()
        result = m.check("OSK-FAKE-KEY")
        assert result.valid is False


class TestSeats:
    def test_activate_seat(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.PERPETUAL, max_seats=2)
        result = m.activate(lic.license_key, "inst-1")
        assert result.valid is True
        assert result.seats_remaining == 1

    def test_activate_over_limit(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.PERPETUAL, max_seats=1)
        m.activate(lic.license_key, "inst-1")
        result = m.activate(lic.license_key, "inst-2")
        assert result.valid is False
        assert "No seats" in result.message

    def test_activate_idempotent(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.PERPETUAL, max_seats=1)
        m.activate(lic.license_key, "inst-1")
        result = m.activate(lic.license_key, "inst-1")
        assert result.valid is True
        assert "Already activated" in result.message

    def test_deactivate_releases_seat(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.PERPETUAL, max_seats=1)
        m.activate(lic.license_key, "inst-1")
        assert m.deactivate(lic.license_key, "inst-1") is True
        result = m.activate(lic.license_key, "inst-2")
        assert result.valid is True

    def test_deactivate_nonexistent(self):
        m = AppLicenseManager()
        assert m.deactivate("fake", "inst-1") is False


class TestRevocation:
    def test_revoke(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.PERPETUAL)
        assert m.revoke(lic.license_key) is True
        result = m.check(lic.license_key)
        assert result.valid is False
        assert result.status == LicenseStatus.REVOKED

    def test_revoke_nonexistent(self):
        m = AppLicenseManager()
        assert m.revoke("fake") is False

    def test_activate_revoked_fails(self):
        m = AppLicenseManager()
        lic = m.issue("app-1", "org-1", LicenseType.PERPETUAL)
        m.revoke(lic.license_key)
        result = m.activate(lic.license_key, "inst-1")
        assert result.valid is False
