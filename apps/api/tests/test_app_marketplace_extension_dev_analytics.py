from app.services.app_marketplace_extension_dev_analytics import ExtDevAnalyticsService

def test_update_and_get():
    svc = ExtDevAnalyticsService()
    svc.update("dev-1", total_extensions=5, total_installs=10000, avg_rating=4.5)
    a = svc.get("dev-1")
    assert a.total_installs == 10000

def test_leaderboard():
    svc = ExtDevAnalyticsService()
    svc.update("dev-1", total_installs=5000)
    svc.update("dev-2", total_installs=15000)
    svc.update("dev-3", total_installs=8000)
    board = svc.get_leaderboard("total_installs", 2)
    assert board[0].developer_id == "dev-2"
    assert len(board) == 2

def test_growth():
    svc = ExtDevAnalyticsService()
    svc.update("dev-1", total_installs=1000, total_revenue_cents=50000, total_reviews=50, total_extensions=3)
    g = svc.get_growth("dev-1")
    assert g["revenue_per_install_cents"] == 50
    assert g["review_rate_pct"] == 5.0
