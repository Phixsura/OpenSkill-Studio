import pytest
from app.services.app_api_developer_api_api_developer_activity_log import AppAPIDeveloperAPIApiDeveloperActivityLog

class TestDeveloperActivityLog:
    def test_record(self):
        l = AppAPIDeveloperAPIApiDeveloperActivityLog()
        e = l.record("inst-1", "a1", "dev1", "key_created", "key-abc")
        assert e.action == "key_created"

    def test_invalid_action(self):
        l = AppAPIDeveloperAPIApiDeveloperActivityLog()
        with pytest.raises(ValueError):
            l.record("inst-1", "a1", "dev1", "hacked", "x")

    def test_by_developer(self):
        l = AppAPIDeveloperAPIApiDeveloperActivityLog()
        l.record("inst-1", "a1", "dev1", "login", "session-1")
        l.record("inst-1", "a2", "dev2", "login", "session-2")
        assert len(l.by_developer("inst-1", "dev1")) == 1

    def test_by_action(self):
        l = AppAPIDeveloperAPIApiDeveloperActivityLog()
        l.record("inst-1", "a1", "dev1", "key_created", "k1")
        l.record("inst-1", "a2", "dev1", "key_revoked", "k1")
        l.record("inst-1", "a3", "dev2", "key_created", "k2")
        assert len(l.by_action("inst-1", "key_created")) == 2

    def test_isolation(self):
        l = AppAPIDeveloperAPIApiDeveloperActivityLog()
        l.record("inst-1", "a1", "dev1", "login", "s1")
        assert l.count("inst-2") == 0
