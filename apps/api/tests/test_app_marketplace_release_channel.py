from app.services.app_marketplace_release_channel import get_channels, promote_release

def test_channels():
    r = get_channels(app_id="a1", versions={"stable": "1.0.0", "beta": "1.1.0-beta.1"})
    assert r["active_channels"] == 2
    stable = next(c for c in r["channels"] if c["id"] == "stable")
    assert stable["current_version"] == "1.0.0"

def test_promote():
    r = promote_release(from_channel="beta", to_channel="stable", version="1.1.0")
    assert r["promoted"]

def test_promote_wrong_direction():
    r = promote_release(from_channel="stable", to_channel="beta", version="1.0.0")
    assert "error" in r
