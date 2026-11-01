from app.services.app_marketplace_app_developer_app_preview import create_preview_link, validate_preview_token, build_preview_page

def test_create():
    p = create_preview_link(app_id="a1", version_id="v1")
    assert "preview.openskill.dev" in p["url"]
    assert len(p["token"]) > 20

def test_validate_ok():
    from datetime import datetime, timezone, timedelta
    stored = {"expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(), "views": 5, "max_views": 100}
    r = validate_preview_token(token="x", stored=stored)
    assert r["valid"]

def test_validate_expired():
    stored = {"expires_at": "2020-01-01T00:00:00+00:00", "views": 0, "max_views": 100}
    r = validate_preview_token(token="x", stored=stored)
    assert not r["valid"]

def test_preview_page():
    p = build_preview_page(app={"name": "App"}, version={"version": "2.0"}, is_preview=True)
    assert p["is_preview"]
    assert p["banner"]
    assert p["actions_disabled"]
