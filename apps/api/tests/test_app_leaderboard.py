"""Tests for App Leaderboard Engine — scores, rankings, history."""

import pytest

from app.services.app_leaderboard import AppLeaderboard


class TestSubmitScore:
    def test_submit(self):
        lb = AppLeaderboard()
        e = lb.submit_score("inst-1", "speed-run", "user-1", 100.0, now=1000.0)
        assert e.score == 100.0
        assert e.user_id == "user-1"

    def test_keeps_personal_best(self):
        lb = AppLeaderboard()
        lb.submit_score("inst-1", "b1", "user-1", 50.0)
        lb.submit_score("inst-1", "b1", "user-1", 80.0)
        lb.submit_score("inst-1", "b1", "user-1", 60.0)
        best = lb.get_personal_best("inst-1", "b1", "user-1")
        assert best is not None
        assert best.score == 80.0

    def test_missing_user_id(self):
        lb = AppLeaderboard()
        with pytest.raises(ValueError, match="user_id"):
            lb.submit_score("inst-1", "b1", "", 10.0)

    def test_missing_board_id(self):
        lb = AppLeaderboard()
        with pytest.raises(ValueError, match="board_id"):
            lb.submit_score("inst-1", "", "user-1", 10.0)


class TestRankings:
    def test_ranked_by_score_desc(self):
        lb = AppLeaderboard()
        lb.submit_score("inst-1", "b1", "alice", 100.0)
        lb.submit_score("inst-1", "b1", "bob", 200.0)
        lb.submit_score("inst-1", "b1", "carol", 150.0)
        rankings = lb.get_rankings("inst-1", "b1")
        assert [r.user_id for r in rankings] == ["bob", "carol", "alice"]
        assert rankings[0].rank == 1

    def test_ascending(self):
        lb = AppLeaderboard()
        lb.submit_score("inst-1", "golf", "alice", 72.0)
        lb.submit_score("inst-1", "golf", "bob", 68.0)
        rankings = lb.get_rankings("inst-1", "golf", ascending=True)
        assert rankings[0].user_id == "bob"

    def test_limit(self):
        lb = AppLeaderboard()
        for i in range(10):
            lb.submit_score("inst-1", "b1", f"user-{i}", float(i))
        rankings = lb.get_rankings("inst-1", "b1", limit=3)
        assert len(rankings) == 3

    def test_empty_board(self):
        lb = AppLeaderboard()
        assert lb.get_rankings("inst-1", "b1") == []


class TestUserRank:
    def test_get_rank(self):
        lb = AppLeaderboard()
        lb.submit_score("inst-1", "b1", "alice", 100.0)
        lb.submit_score("inst-1", "b1", "bob", 200.0)
        assert lb.get_user_rank("inst-1", "b1", "bob") == 1
        assert lb.get_user_rank("inst-1", "b1", "alice") == 2

    def test_not_on_board(self):
        lb = AppLeaderboard()
        assert lb.get_user_rank("inst-1", "b1", "nobody") is None


class TestHistory:
    def test_history_newest_first(self):
        lb = AppLeaderboard()
        lb.submit_score("inst-1", "b1", "user-1", 10.0, now=1000.0)
        lb.submit_score("inst-1", "b1", "user-1", 20.0, now=1001.0)
        lb.submit_score("inst-1", "b1", "user-1", 15.0, now=1002.0)
        h = lb.get_history("inst-1", "b1", "user-1")
        assert [e.score for e in h] == [15.0, 20.0, 10.0]

    def test_history_limit(self):
        lb = AppLeaderboard()
        for i in range(10):
            lb.submit_score("inst-1", "b1", "user-1", float(i))
        h = lb.get_history("inst-1", "b1", "user-1", limit=3)
        assert len(h) == 3


class TestBoardInfo:
    def test_board_size(self):
        lb = AppLeaderboard()
        lb.submit_score("inst-1", "b1", "alice", 10.0)
        lb.submit_score("inst-1", "b1", "bob", 20.0)
        assert lb.board_size("inst-1", "b1") == 2

    def test_list_boards(self):
        lb = AppLeaderboard()
        lb.submit_score("inst-1", "speed", "u1", 10.0)
        lb.submit_score("inst-1", "accuracy", "u1", 95.0)
        assert lb.list_boards("inst-1") == ["accuracy", "speed"]


class TestIsolation:
    def test_cross_installation(self):
        lb = AppLeaderboard()
        lb.submit_score("inst-1", "b1", "user-1", 100.0)
        assert lb.get_personal_best("inst-2", "b1", "user-1") is None
