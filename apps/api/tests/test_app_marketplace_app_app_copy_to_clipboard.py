from app.services.app_marketplace_app_app_copy_to_clipboard import format_for_copy, generate_share_text

def test_markdown():
    r = format_for_copy(content="npm install @openskill/sdk", format_type="markdown")
    assert "```" in r["formatted"]

def test_curl():
    r = format_for_copy(content="https://api.openskill.dev/apps", format_type="curl")
    assert "curl" in r["formatted"]

def test_html_escaping():
    r = format_for_copy(content="<script>", format_type="html")
    assert "<script>" not in r["formatted"]
    assert "&lt;script&gt;" in r["formatted"]

def test_share():
    r = generate_share_text(app_name="Auth SDK", app_url="https://example.com", tagline="Easy auth")
    assert "Auth SDK" in r["twitter"]
    assert "Auth SDK" in r["linkedin"]
    assert r["email"]["subject"] == "Check out Auth SDK"
