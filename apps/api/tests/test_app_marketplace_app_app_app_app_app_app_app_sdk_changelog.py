from app.services.app_marketplace_app_app_app_app_app_app_app_sdk_changelog import build_sdk_changelog

def test_changelog():
    r = build_sdk_changelog([
        {"language": "typescript", "version": "3.5.0", "date": "2026-10-24",
         "changes": ["Added SSO", "Fixed auth bug"], "breaking": False},
        {"language": "typescript", "version": "3.4.0", "date": "2026-10-01",
         "changes": ["New webhooks API"], "breaking": False},
        {"language": "python", "version": "3.5.0", "date": "2026-10-24",
         "changes": ["Async support"], "breaking": True},
    ])
    assert len(r["languages"]) == 2
    assert r["total_releases"] == 3
    assert r["latest"]["typescript"] == "3.5.0"
    assert r["latest"]["python"] == "3.5.0"
