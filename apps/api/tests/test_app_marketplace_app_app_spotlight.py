from app.services.app_marketplace_app_app_spotlight import create_spotlight, get_past_spotlights

def test_create():
    app = {"id": "a1", "name": "Auth SDK", "category": "security", "avg_rating": 4.8,
           "install_count": 5000, "review_count": 120}
    r = create_spotlight(app=app, curator_note="Best auth solution", week="2026-W43")
    assert r["app_name"] == "Auth SDK"
    assert r["week"] == "2026-W43"
    assert len(r["highlights"]) == 3

def test_past():
    spotlights = [{"week": "2026-W43"}, {"week": "2026-W42"}, {"week": "2026-W41"}]
    r = get_past_spotlights(spotlights=spotlights, limit=2)
    assert len(r["spotlights"]) == 2
    assert r["spotlights"][0]["week"] == "2026-W43"
