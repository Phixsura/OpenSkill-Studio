from app.services.app_marketplace_release_channel import assign_channel, get_latest_by_channel, promote_to_stable, list_channels_summary

def test_assign():
    r = assign_channel(version_id="v1", channel="beta", promoted_by="d1")
    assert r["channel"] == "beta"

def test_invalid_channel():
    r = assign_channel(version_id="v1", channel="nightly", promoted_by="d1")
    assert r["error"]

def test_latest():
    versions = [
        {"version": "1.0", "channel": "stable", "released_at": "2026-01-01"},
        {"version": "2.0", "channel": "stable", "released_at": "2026-06-01"},
        {"version": "3.0-beta", "channel": "beta", "released_at": "2026-07-01"},
    ]
    latest = get_latest_by_channel(versions=versions, channel="stable")
    assert latest["version"] == "2.0"

def test_promote():
    r = promote_to_stable(version={"version": "2.0-beta", "channel": "beta"})
    assert r["channel"] == "stable"

def test_promote_invalid():
    r = promote_to_stable(version={"version": "1.0", "channel": "canary"})
    assert r["error"]

def test_summary():
    versions = [{"channel": "stable", "version": "1.0", "released_at": "2026-01-01"},
                {"channel": "beta", "version": "2.0", "released_at": "2026-06-01"}]
    s = list_channels_summary(versions=versions)
    assert len(s) == 2
