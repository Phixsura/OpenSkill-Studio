from app.services.app_marketplace_app_secret_scanner import scan_content

def test_aws_key():
    r = scan_content(content='aws_key = "AKIAIOSFODNN7EXAMPLE"', filename="config.py")
    assert r["total"] >= 1
    assert r["has_critical"]

def test_github_token():
    r = scan_content(content='token = "ghp_ABCDEFghijklmnopqrstuvwxyz1234567890"')
    assert r["total"] >= 1

def test_clean():
    r = scan_content(content='const name = "hello world";')
    assert r["clean"]
    assert r["total"] == 0

def test_private_key():
    r = scan_content(content='-----BEGIN RSA PRIVATE KEY-----\nMIIE...')
    assert r["has_critical"]
