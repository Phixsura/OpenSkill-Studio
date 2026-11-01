from app.services.app_install_analytics import compute_install_trend, compute_retention

def test_trend():
    events = [{"type": "install", "date": "2026-01-01"}, {"type": "install", "date": "2026-01-01"},
              {"type": "uninstall", "date": "2026-01-01"}, {"type": "install", "date": "2026-01-02"}]
    trend = compute_install_trend(events)
    assert trend[0]["net"] == 1  # 2 installs - 1 uninstall
    assert trend[1]["net"] == 1

def test_retention():
    r = compute_retention(installs=[{} for _ in range(100)], uninstalls=[{} for _ in range(20)])
    assert r["retention_rate"] == 80.0

def test_retention_empty():
    r = compute_retention(installs=[], uninstalls=[])
    assert r["retention_rate"] == 100
