from app.services.app_marketplace_app_app_link_checker import extract_links, validate_links, scan_markdown

def test_extract():
    text = "Visit https://example.com and http://docs.example.com/guide for info"
    urls = extract_links(text=text)
    assert len(urls) == 2

def test_validate():
    r = validate_links(urls=["https://example.com", "https://docs.test.com"])
    assert r["valid"] == 2
    assert r["broken"] == 0
    assert r["health"] == "good"

def test_scan_markdown():
    md = "# Docs\nSee https://example.com and https://api.test.com/v1"
    r = scan_markdown(markdown=md)
    assert r["total"] == 2
    assert r["valid"] == 2
