"""Tests for App API Consumer Group — create, members, find."""

import pytest

from app.services.app_api_consumer_group import AppAPIConsumerGroup


class TestCreate:
    def test_create(self):
        g = AppAPIConsumerGroup()
        grp = g.create_group("inst-1", "g1", "VIP Clients", rate_limit=5000)
        assert grp.member_count == 0

    def test_duplicate(self):
        g = AppAPIConsumerGroup()
        g.create_group("inst-1", "g1", "A")
        with pytest.raises(ValueError, match="already exists"):
            g.create_group("inst-1", "g1", "B")


class TestMembers:
    def test_add_remove(self):
        g = AppAPIConsumerGroup()
        g.create_group("inst-1", "g1", "VIP")
        g.add_member("inst-1", "g1", "consumer-a")
        g.add_member("inst-1", "g1", "consumer-b")
        assert g.list_groups("inst-1")[0].member_count == 2
        g.remove_member("inst-1", "g1", "consumer-a")
        assert g.list_groups("inst-1")[0].member_count == 1

    def test_find_groups(self):
        g = AppAPIConsumerGroup()
        g.create_group("inst-1", "g1", "VIP")
        g.create_group("inst-1", "g2", "Beta")
        g.add_member("inst-1", "g1", "consumer-a")
        g.add_member("inst-1", "g2", "consumer-a")
        groups = g.find_groups("inst-1", "consumer-a")
        assert len(groups) == 2


class TestIsolation:
    def test_cross(self):
        g = AppAPIConsumerGroup()
        g.create_group("inst-1", "g1", "VIP")
        assert g.list_groups("inst-2") == []
