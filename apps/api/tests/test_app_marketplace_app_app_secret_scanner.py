from app.services.app_marketplace_app_app_secret_scanner import scan_text, scan_files

def test_aws_key():
    r = scan_text(text="aws_key = AKIAIOSFODNN7EXAMPLE", filename="config.py")
    assert r["has_secrets"]
    assert r["findings"][0]["type"] == "aws_key"
    assert r["findings"][0]["severity"] == "critical"

def test_generic_secret():
    r = scan_text(text='password = "mysuperpassword123"')
    assert r["has_secrets"]
    assert r["findings"][0]["type"] == "generic_secret"

def test_clean():
    r = scan_text(text="const x = 42;\nconst y = 'hello';")
    assert not r["has_secrets"]

def test_scan_files():
    files = [
        {"name": "clean.py", "content": "x = 1"},
        {"name": "bad.py", "content": 'secret = "mysupersecretvalue"'},
    ]
    r = scan_files(files=files)
    assert r["files_scanned"] == 2
    assert r["files_with_secrets"] == 1
    assert not r["clean"]
