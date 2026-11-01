from app.services.app_marketplace_app_app_app_app_app_app_app_secret_scanner import scan_content, scan_files

def test_scan_aws():
    r = scan_content('AWS_KEY = "AKIAIOSFODNN7EXAMPLE"', filename="config.py")
    assert r["has_secrets"]
    assert r["count"] == 1
    assert r["findings"][0]["type"] == "aws_key"
    assert r["findings"][0]["severity"] == "critical"

def test_scan_clean():
    r = scan_content('name = "hello"\nport = 8080', filename="app.py")
    assert not r["has_secrets"]
    assert r["count"] == 0

def test_scan_files():
    files = {
        "clean.py": "x = 1",
        "leak.py": 'token = "AKIAIOSFODNN7EXAMPLE"',
    }
    r = scan_files(files)
    assert r["total_files"] == 2
    assert r["total_findings"] == 2  # aws_key + generic_secret
    assert not r["clean"]
