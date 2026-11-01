from app.services.app_marketplace_extension_connector_auth import (
    ConnectorAuthService, AuthType, ConnectionStatus,
)


def test_store_and_verify_api_key():
    svc = ConnectorAuthService()
    cred = svc.store_api_key("slack", "ext-1", "xoxb-secret-key")
    assert cred.auth_type == AuthType.API_KEY
    assert cred.status == ConnectionStatus.CONNECTED
    assert svc.verify_api_key(cred.credential_id, "xoxb-secret-key") is True
    assert svc.verify_api_key(cred.credential_id, "wrong-key") is False


def test_store_oauth2():
    svc = ConnectorAuthService()
    cred = svc.store_oauth2("github", "ext-1", "access_tok", "refresh_tok",
                            3600, ["repo", "user"])
    assert cred.auth_type == AuthType.OAUTH2
    assert cred.scopes == ["repo", "user"]


def test_token_expiry():
    svc = ConnectorAuthService()
    cred = svc.store_oauth2("github", "ext-1", "tok", "ref", -1, [])
    assert svc.is_token_expired(cred.credential_id) is True


def test_refresh_oauth2():
    svc = ConnectorAuthService()
    cred = svc.store_oauth2("github", "ext-1", "old_tok", "old_ref", -1, [])
    assert svc.refresh_oauth2(cred.credential_id, "new_tok", "new_ref", 3600) is True
    assert svc.is_token_expired(cred.credential_id) is False


def test_disconnect():
    svc = ConnectorAuthService()
    cred = svc.store_api_key("slack", "ext-1", "key")
    svc.disconnect(cred.credential_id)
    status = svc.get_status(cred.credential_id)
    assert status["status"] == "disconnected"


def test_credential_hash_stored():
    svc = ConnectorAuthService()
    cred = svc.store_api_key("slack", "ext-1", "secret")
    # Raw credential should NOT be stored
    assert "secret" not in cred.credential_hash
    assert len(cred.credential_hash) == 64  # SHA-256 hex


def test_list_credentials():
    svc = ConnectorAuthService()
    svc.store_api_key("slack", "ext-1", "k1")
    svc.store_oauth2("github", "ext-1", "t", "r", 3600, [])
    svc.store_api_key("jira", "ext-2", "k2")
    creds = svc.list_credentials("ext-1")
    assert len(creds) == 2
