from app.services.app_marketplace_app_app_digest_builder import build_digest

def test_digest():
    events = [
        {"type": "install", "title": "App installed", "timestamp": "2026-01-01"},
        {"type": "review", "title": "New review", "timestamp": "2026-01-01"},
        {"type": "install", "title": "Another install", "timestamp": "2026-01-02"},
    ]
    r = build_digest(events=events, period="weekly")
    assert r["total_events"] == 3
    assert r["section_count"] == 2
    assert "weekly" in r["subject"]
    install_section = next(s for s in r["sections"] if s["type"] == "install")
    assert install_section["count"] == 2

def test_empty():
    r = build_digest(events=[])
    assert r["total_events"] == 0
