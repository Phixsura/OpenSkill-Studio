from app.services.app_marketplace_extension_developer_leaderboard import (
    DeveloperLeaderboardService, LeaderboardMetric,
)


def test_update_and_rank():
    svc = DeveloperLeaderboardService()
    svc.update("d1", "Alice", installs=5000, avg_rating=4.8, extensions=10)
    svc.update("d2", "Bob", installs=10000, avg_rating=4.2, extensions=5)
    board = svc.get_leaderboard(LeaderboardMetric.INSTALLS, 2)
    assert board[0]["name"] == "Bob"
    assert board[0]["rank"] == 1


def test_rating_leaderboard():
    svc = DeveloperLeaderboardService()
    svc.update("d1", "Alice", avg_rating=4.9)
    svc.update("d2", "Bob", avg_rating=4.5)
    board = svc.get_leaderboard(LeaderboardMetric.RATING)
    assert board[0]["name"] == "Alice"


def test_composite_score():
    svc = DeveloperLeaderboardService()
    svc.update("d1", "Alice", installs=1000, avg_rating=4.5, extensions=5, revenue_cents=50000)
    rank = svc.get_rank("d1")
    assert rank["rank"] == 1
    assert rank["score"] > 0


def test_percentile():
    svc = DeveloperLeaderboardService()
    for i in range(10):
        svc.update(f"d{i}", f"Dev{i}", installs=i * 100)
    rank = svc.get_rank("d9")  # highest installs
    assert rank["percentile"] == 100.0
