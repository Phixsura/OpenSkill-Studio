from app.services.app_marketplace_app_app_404_handler import log_404, analyze_404s

def test_log():
    r = log_404(path="/missing-page", referrer="https://google.com")
    assert r["path"] == "/missing-page"

def test_analyze():
    logs = [
        {"path": "/old-page", "referrer": "https://google.com"},
        {"path": "/old-page", "referrer": "https://google.com"},
        {"path": "/typo", "referrer": ""},
    ]
    r = analyze_404s(logs=logs)
    assert r["total"] == 3
    assert r["unique_paths"] == 2
    assert r["top_paths"][0]["path"] == "/old-page"
    assert r["top_paths"][0]["count"] == 2
