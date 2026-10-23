from app.services.app_marketplace_app_app_app_app_app_app_app_cors_policy import create_policy, check_origin

def test_create():
    p = create_policy(["https://app.com", "https://admin.app.com"], ["GET", "POST"], allow_credentials=True)
    assert p["created"]
    assert len(p["origins"]) == 2

def test_wildcard_creds():
    p = create_policy(["*"], allow_credentials=True)
    assert not p["created"]
    assert "wildcard" in p["error"]

def test_check():
    p = create_policy(["https://app.com"])
    assert check_origin(p, "https://app.com")["allowed"]
    assert not check_origin(p, "https://evil.com")["allowed"]
