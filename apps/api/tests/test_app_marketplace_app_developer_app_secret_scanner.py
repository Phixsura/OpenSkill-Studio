from app.services.app_marketplace_app_developer_app_secret_scanner import scan_content, scan_files

def test_aws_key():
    r = scan_content(content='aws_key = "AKIAIOSFODNN7EXAMPLE"', filename="config.py")
    assert len(r) == 1
    assert r[0]["type"] == "AWS Access Key"
    assert r[0]["severity"] == "critical"

def test_private_key():
    r = scan_content(content="-----BEGIN RSA PRIVATE KEY-----\nMIIE...", filename="key.pem")
    assert len(r) == 1

def test_db_url():
    r = scan_content(content='DATABASE_URL=postgres://user:pass@host:5432/db', filename=".env")
    assert len(r) == 1
    assert r[0]["severity"] == "critical"

def test_clean():
    r = scan_content(content="console.log('hello world')", filename="app.js")
    assert len(r) == 0

def test_scan_files():
    files = {"config.py": 'KEY = "AKIAIOSFODNN7EXAMPLE"', "app.js": "console.log('ok')"}
    r = scan_files(files=files)
    assert r["total"] == 1
    assert r["files_scanned"] == 2
    assert not r["clean"]
