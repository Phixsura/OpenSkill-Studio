"""Tests for App Invite Link — create, claim, revoke."""

import pytest

from app.services.app_invite_link import AppInviteLink


class TestCreate:
    def test_create(self):
        i = AppInviteLink()
        link = i.create("inst-1", "inv-1", role="admin", max_uses=5)
        assert link.is_valid is True
        assert len(link.code) > 10

    def test_server_generated_code(self):
        i = AppInviteLink()
        l1 = i.create("inst-1", "inv-1")
        l2 = i.create("inst-1", "inv-2")
        assert l1.code != l2.code


class TestClaim:
    def test_claim(self):
        i = AppInviteLink()
        link = i.create("inst-1", "inv-1")
        claimed = i.claim("inst-1", link.code)
        assert claimed.uses == 1

    def test_max_uses(self):
        i = AppInviteLink()
        link = i.create("inst-1", "inv-1", max_uses=1)
        i.claim("inst-1", link.code)
        with pytest.raises(ValueError, match="no longer valid"):
            i.claim("inst-1", link.code)

    def test_invalid_code(self):
        i = AppInviteLink()
        with pytest.raises(KeyError):
            i.claim("inst-1", "bad-code")


class TestRevoke:
    def test_revoke(self):
        i = AppInviteLink()
        link = i.create("inst-1", "inv-1")
        i.revoke("inst-1", "inv-1")
        with pytest.raises(ValueError, match="no longer valid"):
            i.claim("inst-1", link.code)


class TestIsolation:
    def test_cross(self):
        i = AppInviteLink()
        i.create("inst-1", "inv-1")
        assert i.list_links("inst-2") == []
