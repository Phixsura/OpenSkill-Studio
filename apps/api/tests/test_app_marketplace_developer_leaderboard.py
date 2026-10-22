from app.services.app_marketplace_developer_leaderboard import build_leaderboard

DEVS = [{"name": "Dev A", "app_count": 5, "total_installs": 200, "avg_health": 95},
        {"name": "Dev B", "app_count": 10, "total_installs": 50, "avg_health": 90}]

def test_ranked():
    lb = build_leaderboard(DEVS)
    assert lb[0]["rank"] == 1
    assert len(lb) == 2

def test_limit():
    lb = build_leaderboard(DEVS, limit=1)
    assert len(lb) == 1
