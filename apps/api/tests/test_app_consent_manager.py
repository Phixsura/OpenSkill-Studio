"""Tests for App Consent Manager — grant, withdraw, check, history."""

import pytest

from app.services.app_consent_manager import AppConsentManager


class TestGrantConsent:
    def test_grant(self):
        m = AppConsentManager()
        r = m.grant_consent("inst-1", "user-1", "analytics", source="signup")
        assert r.granted is True
        assert r.purpose == "analytics"

    def test_missing_purpose(self):
        m = AppConsentManager()
        with pytest.raises(ValueError, match="purpose"):
            m.grant_consent("inst-1", "user-1", "")


class TestWithdrawConsent:
    def test_withdraw(self):
        m = AppConsentManager()
        m.grant_consent("inst-1", "user-1", "marketing")
        r = m.withdraw_consent("inst-1", "user-1", "marketing")
        assert r.granted is False


class TestHasConsent:
    def test_granted(self):
        m = AppConsentManager()
        m.grant_consent("inst-1", "user-1", "analytics")
        assert m.has_consent("inst-1", "user-1", "analytics") is True

    def test_withdrawn(self):
        m = AppConsentManager()
        m.grant_consent("inst-1", "user-1", "analytics")
        m.withdraw_consent("inst-1", "user-1", "analytics")
        assert m.has_consent("inst-1", "user-1", "analytics") is False

    def test_no_record(self):
        m = AppConsentManager()
        assert m.has_consent("inst-1", "user-1", "analytics") is False

    def test_regrant(self):
        m = AppConsentManager()
        m.grant_consent("inst-1", "user-1", "analytics")
        m.withdraw_consent("inst-1", "user-1", "analytics")
        m.grant_consent("inst-1", "user-1", "analytics")
        assert m.has_consent("inst-1", "user-1", "analytics") is True


class TestUserConsents:
    def test_multiple_purposes(self):
        m = AppConsentManager()
        m.grant_consent("inst-1", "user-1", "analytics")
        m.grant_consent("inst-1", "user-1", "marketing")
        m.withdraw_consent("inst-1", "user-1", "marketing")
        consents = m.get_user_consents("inst-1", "user-1")
        assert consents == {"analytics": True, "marketing": False}


class TestHistory:
    def test_history_newest_first(self):
        m = AppConsentManager()
        m.grant_consent("inst-1", "user-1", "analytics", now=1000.0)
        m.withdraw_consent("inst-1", "user-1", "analytics", now=1001.0)
        h = m.get_consent_history("inst-1", "user-1", "analytics")
        assert len(h) == 2
        assert h[0].granted is False  # newest


class TestConsentedUsers:
    def test_list(self):
        m = AppConsentManager()
        m.grant_consent("inst-1", "user-1", "analytics")
        m.grant_consent("inst-1", "user-2", "analytics")
        m.grant_consent("inst-1", "user-3", "analytics")
        m.withdraw_consent("inst-1", "user-2", "analytics")
        users = m.get_consented_users("inst-1", "analytics")
        assert users == ["user-1", "user-3"]


class TestIsolation:
    def test_cross_installation(self):
        m = AppConsentManager()
        m.grant_consent("inst-1", "user-1", "analytics")
        assert m.has_consent("inst-2", "user-1", "analytics") is False
