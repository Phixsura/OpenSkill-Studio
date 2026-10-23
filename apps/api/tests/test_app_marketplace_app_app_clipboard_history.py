from app.services.app_marketplace_app_app_clipboard_history import ClipboardHistory

def test_add_and_list():
    h = ClipboardHistory(max_size=5)
    h.add(content="hello world", source="copy")
    h.add(content="foo bar")
    r = h.list_items(limit=10)
    assert r["total"] == 2
    assert r["items"][0]["content"] == "foo bar"  # newest first

def test_max_size():
    h = ClipboardHistory(max_size=3)
    for i in range(5):
        h.add(content=f"item {i}")
    r = h.list_items()
    assert r["total"] == 3

def test_search():
    h = ClipboardHistory()
    h.add(content="const x = 42;")
    h.add(content="function hello() {}")
    results = h.search(query="const")
    assert len(results) == 1

def test_clear():
    h = ClipboardHistory()
    h.add(content="a")
    h.add(content="b")
    r = h.clear()
    assert r["cleared"] == 2
    assert h.list_items()["total"] == 0
