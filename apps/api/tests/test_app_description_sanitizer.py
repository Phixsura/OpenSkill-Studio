from app.services.app_description_sanitizer import sanitize_description, validate_description

def test_clean_text():
    assert sanitize_description("Hello world") == "Hello world"

def test_strip_html():
    assert sanitize_description("Hello <b>world</b>") == "Hello world"

def test_strip_script():
    assert "alert" not in sanitize_description("Hi<script>alert(1)</script>there")

def test_none():
    assert sanitize_description(None) is None

def test_truncate():
    long = "x" * 3000
    assert len(sanitize_description(long)) <= 2000

def test_validate_script():
    errors = validate_description("<script>evil()</script>")
    assert any("script" in e for e in errors)

def test_validate_ok():
    assert validate_description("Normal description") == []

def test_validate_long():
    assert len(validate_description("x" * 3000)) > 0
