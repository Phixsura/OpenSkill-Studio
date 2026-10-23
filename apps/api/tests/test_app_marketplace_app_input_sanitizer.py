from app.services.app_marketplace_app_input_sanitizer import sanitize_html_input, detect_sql_injection, detect_command_injection, sanitize_filename

def test_html_escape():
    r = sanitize_html_input(value='<script>alert("xss")</script>')
    assert "<script>" not in r
    assert "&lt;script&gt;" in r

def test_sql_safe():
    r = detect_sql_injection(value="normal search query")
    assert r["safe"]

def test_sql_injection():
    r = detect_sql_injection(value="' OR '1'='1")
    assert not r["safe"]

def test_union_select():
    r = detect_sql_injection(value="1 UNION SELECT * FROM users")
    assert not r["safe"]

def test_cmd_safe():
    r = detect_command_injection(value="hello world")
    assert r["safe"]

def test_cmd_injection():
    r = detect_command_injection(value="file; rm -rf /")
    assert not r["safe"]
    assert ";" in r["dangerous_chars"]

def test_filename():
    assert sanitize_filename(filename="../../etc/passwd") == "etcpasswd"
    assert sanitize_filename(filename="my file (1).txt") == "my_file__1_.txt"
    assert sanitize_filename(filename="normal.jpg") == "normal.jpg"
