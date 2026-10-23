from app.services.app_marketplace_app_app_app_app_app_app_app_md_renderer import render_markdown

def test_render():
    md = """# Hello World

This is a paragraph.

## Code Example

```python
print("hello")
```

Another paragraph.
"""
    r = render_markdown(md)
    assert r["block_count"] == 5
    assert r["blocks"][0]["type"] == "heading"
    assert r["blocks"][0]["level"] == 1
    assert r["blocks"][1]["type"] == "paragraph"
    assert r["blocks"][2]["type"] == "heading"
    assert r["blocks"][3]["type"] == "code"
    assert r["blocks"][3]["language"] == "python"
    assert r["blocks"][4]["type"] == "paragraph"
    assert r["read_time_min"] >= 1
