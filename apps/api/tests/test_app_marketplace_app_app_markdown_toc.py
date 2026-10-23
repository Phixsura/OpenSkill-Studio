from app.services.app_marketplace_app_app_markdown_toc import extract_toc

MD = """# Getting Started
## Installation
### Prerequisites
## Usage
# API Reference
## Methods
"""

def test_toc():
    r = extract_toc(markdown=MD)
    assert r["count"] == 6
    assert r["max_depth"] == 3
    assert r["items"][0]["text"] == "Getting Started"
    assert r["items"][0]["slug"] == "getting-started"
    assert r["items"][2]["level"] == 3

def test_empty():
    r = extract_toc(markdown="No headings here")
    assert r["count"] == 0

def test_xss():
    r = extract_toc(markdown="# <script>alert(1)</script>")
    assert "<script>" not in r["items"][0]["text"]
