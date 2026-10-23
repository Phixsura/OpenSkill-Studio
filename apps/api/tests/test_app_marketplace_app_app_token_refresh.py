from app.services.app_marketplace_app_app_token_refresh import create_token_pair, rotate_refresh_token, is_token_expired

def test_create_pair():
    r = create_token_pair(user_id="u1")
    assert len(r["access_token"]) > 20
    assert len(r["refresh_token"]) > 30
    assert r["token_type"] == "Bearer"

def test_rotate():
    pair = create_token_pair(user_id="u1")
    r = rotate_refresh_token(old_refresh=pair["refresh_token"])
    assert r["rotated"]
    assert r["old_invalidated"]
    assert r["access_token"] != pair["access_token"]
    assert r["refresh_token"] != pair["refresh_token"]

def test_expired():
    assert is_token_expired(expires_at="2020-01-01T00:00:00+00:00")
    assert not is_token_expired(expires_at="2099-01-01T00:00:00+00:00")
