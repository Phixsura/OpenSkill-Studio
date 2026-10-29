import pytest
from app.services.app_api_developer_profile import AppAPIDeveloperProfile

class TestProfile:
    def test_create(self):
        p = AppAPIDeveloperProfile()
        prof = p.create("inst-1", "alice", "Alice Smith", "alice@dev.com", "Full-stack dev")
        assert prof.display_name == "Alice Smith"

    def test_update(self):
        p = AppAPIDeveloperProfile()
        p.create("inst-1", "alice", "Alice", "alice@dev.com")
        p.update("inst-1", "alice", bio="Updated bio", app_count=3)
        assert p.get("inst-1", "alice").bio == "Updated bio"

    def test_search(self):
        p = AppAPIDeveloperProfile()
        p.create("inst-1", "alice", "Alice Smith", "alice@dev.com")
        p.create("inst-1", "bob", "Bob Jones", "bob@dev.com")
        assert len(p.search("inst-1", "alice")) == 1

    def test_isolation(self):
        p = AppAPIDeveloperProfile()
        p.create("inst-1", "alice", "Alice", "a@b.com")
        assert p.list_profiles("inst-2") == []
