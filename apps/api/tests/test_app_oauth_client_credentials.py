from app.services.app_oauth_client_credentials import generate_client_credentials, verify_client_secret, generate_access_token

def test_generate_credentials():
    creds = generate_client_credentials()
    assert creds["client_id"].startswith("osk_")
    assert len(creds["client_secret"]) > 20
    assert len(creds["secret_hash"]) == 64

def test_verify_correct():
    creds = generate_client_credentials()
    assert verify_client_secret(creds["client_secret"], creds["secret_hash"]) is True

def test_verify_wrong():
    creds = generate_client_credentials()
    assert verify_client_secret("wrong_secret", creds["secret_hash"]) is False

def test_unique_credentials():
    ids = {generate_client_credentials()["client_id"] for _ in range(20)}
    assert len(ids) == 20

def test_access_token():
    token = generate_access_token(client_id="osk_test", scopes=["read:cohorts"])
    assert token["access_token"].startswith("osk_at_")
    assert token["token_type"] == "bearer"
    assert token["expires_in"] == 3600

def test_access_token_scopes():
    token = generate_access_token(client_id="x", scopes=["write:projects", "read:cohorts"])
    assert token["scope"] == "read:cohorts write:projects"  # sorted
