from app.services.app_marketplace_app_markdown_renderer import render_markdown, extract_headings

def test_render():
    r = render_markdown(text="# Hello\n\nThis is **bold** and *italic*.")
    assert "<h1>Hello</h1>" in r["html"]
    assert "<strong>bold</strong>" in r["html"]
    assert "<em>italic</em>" in r["html"]

def test_code():
    r = render_markdown(text="Use `npm install` to install.")
    assert "<code>npm install</code>" in r["html"]

def test_xss():
    r = render_markdown(text="<script>alert(1)</script>")
    assert "<script>" not in r["html"]
    assert "&lt;script&gt;" in r["html"]

def test_headings():
    r = extract_headings(text="# Intro\n## Setup\n### Details\nText")
    assert r["total"] == 3
    assert r["headings"][0]["level"] == 1
    assert r["headings"][1]["text"] == "Setup"
