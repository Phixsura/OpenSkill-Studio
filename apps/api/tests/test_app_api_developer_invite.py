import pytest
from app.services.app_api_developer_invite import AppAPIDeveloperInvite

class TestInvite:
    def test_create(self):
        i = AppAPIDeveloperInvite()
        inv = i.create("inst-1", "i1", "dev@example.com")
        assert len(inv.code) > 10
        assert inv.accepted is False

    def test_accept(self):
        i = AppAPIDeveloperInvite()
        inv = i.create("inst-1", "i1", "dev@example.com")
        accepted = i.accept("inst-1", inv.code)
        assert accepted.accepted is True
        assert i.pending("inst-1") == []

    def test_invalid_code(self):
        i = AppAPIDeveloperInvite()
        with pytest.raises(KeyError):
            i.accept("inst-1", "bad-code")

    def test_invalid_email(self):
        i = AppAPIDeveloperInvite()
        with pytest.raises(ValueError):
            i.create("inst-1", "i1", "not-email")

    def test_isolation(self):
        i = AppAPIDeveloperInvite()
        i.create("inst-1", "i1", "a@b.com")
        assert i.list_invites("inst-2") == []
