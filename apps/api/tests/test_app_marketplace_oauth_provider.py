from app.services.app_marketplace_oauth_provider import OAuthProvider


def test_register_client():
    oauth = OAuthProvider()
    result = oauth.register_client("c1", "My App", ["https://app.test/cb"],
                                    ["read", "write"], "dev-1")
    assert result["client_id"] == "c1"
    assert "client_secret" in result
    assert oauth.get_client("c1") is not None


def test_full_oauth_flow():
    oauth = OAuthProvider()
    reg = oauth.register_client("c2", "Test App", ["https://app.test/cb"],
                                 ["read", "write"], "dev-2")
    # Step 1: Authorize
    auth = oauth.authorize("c2", "user-1", ["read"], "https://app.test/cb")
    assert auth is not None
    assert "code" in auth

    # Step 2: Exchange code for token
    token_resp = oauth.exchange_code(auth["code"], "c2", reg["client_secret"])
    assert token_resp is not None
    assert "access_token" in token_resp
    assert token_resp["token_type"] == "bearer"

    # Step 3: Validate token
    claims = oauth.validate_token(token_resp["access_token"])
    assert claims is not None
    assert claims["user_id"] == "user-1"
    assert "read" in claims["scopes"]


def test_invalid_redirect_uri():
    oauth = OAuthProvider()
    oauth.register_client("c3", "App", ["https://good.com/cb"], ["read"], "dev")
    result = oauth.authorize("c3", "user", ["read"], "https://evil.com/cb")
    assert result is None


def test_invalid_scope():
    oauth = OAuthProvider()
    oauth.register_client("c4", "App", ["https://app.com/cb"], ["read"], "dev")
    result = oauth.authorize("c4", "user", ["admin"], "https://app.com/cb")
    assert result is None


def test_code_reuse_blocked():
    oauth = OAuthProvider()
    reg = oauth.register_client("c5", "App", ["https://app.com/cb"], ["read"], "dev")
    auth = oauth.authorize("c5", "user", ["read"], "https://app.com/cb")
    oauth.exchange_code(auth["code"], "c5", reg["client_secret"])
    second = oauth.exchange_code(auth["code"], "c5", reg["client_secret"])
    assert second is None  # code already used


def test_revoke_token():
    oauth = OAuthProvider()
    reg = oauth.register_client("c6", "App", ["https://a.com/cb"], ["read"], "dev")
    auth = oauth.authorize("c6", "user", ["read"], "https://a.com/cb")
    token_resp = oauth.exchange_code(auth["code"], "c6", reg["client_secret"])
    assert oauth.revoke_token(token_resp["access_token"]) is True
    assert oauth.validate_token(token_resp["access_token"]) is None
