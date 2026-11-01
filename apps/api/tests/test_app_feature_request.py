"""Tests for App Feature Request — submit, vote, status, ranking."""

import pytest

from app.services.app_feature_request import AppFeatureRequest, RequestStatus


class TestSubmit:
    def test_submit(self):
        f = AppFeatureRequest()
        r = f.submit("inst-1", "r1", "Dark Mode", "Add dark theme", "alice")
        assert r.vote_count == 1  # auto-upvote
        assert r.status == RequestStatus.OPEN


class TestVote:
    def test_vote(self):
        f = AppFeatureRequest()
        f.submit("inst-1", "r1", "Feature", "Desc", "alice")
        f.vote("inst-1", "r1", "bob")
        f.vote("inst-1", "r1", "charlie")
        r = f.list_all("inst-1")[0]
        assert r.vote_count == 3

    def test_deduplicate(self):
        f = AppFeatureRequest()
        f.submit("inst-1", "r1", "Feature", "Desc", "alice")
        f.vote("inst-1", "r1", "alice")  # duplicate
        assert f.list_all("inst-1")[0].vote_count == 1


class TestRanking:
    def test_top_voted(self):
        f = AppFeatureRequest()
        f.submit("inst-1", "r1", "A", "D", "alice")
        f.submit("inst-1", "r2", "B", "D", "alice")
        f.vote("inst-1", "r2", "bob")
        f.vote("inst-1", "r2", "charlie")
        top = f.top_voted("inst-1")
        assert top[0].request_id == "r2"


class TestStatus:
    def test_update(self):
        f = AppFeatureRequest()
        f.submit("inst-1", "r1", "Feature", "Desc", "alice")
        r = f.update_status("inst-1", "r1", RequestStatus.PLANNED)
        assert r.status == RequestStatus.PLANNED


class TestIsolation:
    def test_cross(self):
        f = AppFeatureRequest()
        f.submit("inst-1", "r1", "Feature", "Desc", "alice")
        assert f.list_all("inst-2") == []
