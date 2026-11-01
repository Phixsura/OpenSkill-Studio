from app.services.app_marketplace_extension_cursor_paginator import CursorPaginatorService


def _items(n):
    return [{"id": i, "name": f"item-{i}"} for i in range(1, n + 1)]


def test_first_page():
    cp = CursorPaginatorService()
    conn = cp.paginate(_items(10), sort_key="id", first=3)
    assert len(conn.edges) == 3
    assert conn.edges[0].node["id"] == 1
    assert conn.page_info.has_next_page is True
    assert conn.page_info.total_count == 10


def test_cursor_round_trip():
    cp = CursorPaginatorService()
    cursor = cp.encode_cursor({"id": 42})
    decoded = cp.decode_cursor(cursor)
    assert decoded["id"] == 42


def test_forward_pagination():
    cp = CursorPaginatorService()
    page1 = cp.paginate(_items(10), sort_key="id", first=3)
    end_cursor = page1.page_info.end_cursor
    page2 = cp.paginate(_items(10), sort_key="id", first=3, after=end_cursor)
    assert page2.edges[0].node["id"] == 4
    assert page2.page_info.has_previous_page is True


def test_last_page_no_next():
    cp = CursorPaginatorService()
    page = cp.paginate(_items(5), sort_key="id", first=10)
    assert page.page_info.has_next_page is False
    assert len(page.edges) == 5


def test_empty():
    cp = CursorPaginatorService()
    conn = cp.paginate([], sort_key="id", first=10)
    assert len(conn.edges) == 0
    assert conn.page_info.start_cursor == ""


def test_descending():
    cp = CursorPaginatorService()
    conn = cp.paginate(_items(10), sort_key="id", first=3, sort_desc=True)
    assert conn.edges[0].node["id"] == 10
    assert conn.edges[2].node["id"] == 8


def test_full_scan():
    cp = CursorPaginatorService()
    items = _items(7)
    all_ids = []
    after = ""
    for _ in range(10):  # safety limit
        page = cp.paginate(items, sort_key="id", first=3, after=after)
        all_ids.extend(e.node["id"] for e in page.edges)
        if not page.page_info.has_next_page:
            break
        after = page.page_info.end_cursor
    assert all_ids == [1, 2, 3, 4, 5, 6, 7]
