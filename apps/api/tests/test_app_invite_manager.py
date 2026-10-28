"""Tests for App Invite Manager — create, accept, decline, revoke, expiry."""

import pytest

from app.services.app_invite_manager import AppInviteManager, InviteStatus


class TestCreateInvite:
    def test_create(self):
        m = AppInviteManager()
        i = m.create_invite("inst-1", "inv-1", "user@example.com", role="admin", now=1000.0)
        assert i.email == "user@example.com"
        assert i.status == InviteStatus.PENDING
        assert len(i.token) > 20

    def test_duplicate(self):
        m = AppInviteManager()
        m.create_invite("inst-1", "inv-1", "a@b.com")
        with pytest.raises(ValueError, match="already exists"):
            m.create_invite("inst-1", "inv-1", "c@d.com")

    def test_missing_email(self):
        m = AppInviteManager()
        with pytest.raises(ValueError, match="email"):
            m.create_invite("inst-1", "inv-1", "")


class TestAccept:
    def test_accept(self):
        m = AppInviteManager()
        inv = m.create_invite("inst-1", "inv-1", "a@b.com", now=1000.0)
        accepted = m.accept_invite(inv.token, "a@b.com", now=1001.0)
        assert accepted.status == InviteStatus.ACCEPTED

    def test_cannot_accept_revoked(self):
        m = AppInviteManager()
        inv = m.create_invite("inst-1", "inv-1", "a@b.com")
        m.revoke_invite("inst-1", "inv-1")
        with pytest.raises(ValueError, match="Cannot accept"):
            m.accept_invite(inv.token, "a@b.com")

    def test_wrong_email_rejected(self):
        m = AppInviteManager()
        inv = m.create_invite("inst-1", "inv-1", "a@b.com")
        with pytest.raises(PermissionError, match="not addressed"):
            m.accept_invite(inv.token, "wrong@other.com")


class TestDecline:
    def test_decline(self):
        m = AppInviteManager()
        inv = m.create_invite("inst-1", "inv-1", "a@b.com")
        declined = m.decline_invite(inv.token, "a@b.com")
        assert declined.status == InviteStatus.DECLINED


class TestRevoke:
    def test_revoke(self):
        m = AppInviteManager()
        m.create_invite("inst-1", "inv-1", "a@b.com")
        revoked = m.revoke_invite("inst-1", "inv-1")
        assert revoked.status == InviteStatus.REVOKED

    def test_cannot_revoke_accepted(self):
        m = AppInviteManager()
        inv = m.create_invite("inst-1", "inv-1", "a@b.com")
        m.accept_invite(inv.token, "a@b.com")
        with pytest.raises(ValueError, match="Cannot revoke"):
            m.revoke_invite("inst-1", "inv-1")


class TestExpiry:
    def test_expired(self):
        m = AppInviteManager(expiry_hours=1)
        inv = m.create_invite("inst-1", "inv-1", "a@b.com", now=1000.0)
        with pytest.raises(ValueError):
            m.accept_invite(inv.token, "a@b.com", now=1000.0 + 3601)


class TestRoleValidation:
    def test_invalid_role(self):
        m = AppInviteManager()
        with pytest.raises(ValueError, match="Invalid role"):
            m.create_invite("inst-1", "inv-1", "a@b.com", role="superadmin")


class TestListInvites:
    def test_list_all(self):
        m = AppInviteManager()
        m.create_invite("inst-1", "inv-1", "a@b.com")
        m.create_invite("inst-1", "inv-2", "c@d.com")
        assert len(m.list_invites("inst-1")) == 2

    def test_filter_by_status(self):
        m = AppInviteManager()
        inv = m.create_invite("inst-1", "inv-1", "a@b.com")
        m.create_invite("inst-1", "inv-2", "c@d.com")
        m.accept_invite(inv.token, "a@b.com")
        pending = m.list_invites("inst-1", status=InviteStatus.PENDING)
        assert len(pending) == 1


class TestIsolation:
    def test_cross_installation(self):
        m = AppInviteManager()
        m.create_invite("inst-1", "inv-1", "a@b.com")
        with pytest.raises(KeyError):
            m._get("inst-2", "inv-1")

    def test_invalid_token(self):
        m = AppInviteManager()
        with pytest.raises(KeyError, match="Invalid"):
            m.accept_invite("bogus-token", "x@y.com")
