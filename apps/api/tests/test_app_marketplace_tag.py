from app.services.app_marketplace_tag import add_tag, remove_tag, get_tags, find_by_tag, popular_tags

def test_add_get():
    add_tag("t1", "analytics")
    add_tag("t1", "dashboard")
    assert "analytics" in get_tags("t1")

def test_find():
    add_tag("t2", "connector")
    assert "t2" in find_by_tag("connector")

def test_remove():
    add_tag("t3", "old")
    remove_tag("t3", "old")
    assert "old" not in get_tags("t3")

def test_popular():
    for i in range(5):
        add_tag(f"pop{i}", "popular-tag")
    tags = popular_tags(limit=5)
    assert any(t["tag"] == "popular-tag" for t in tags)

def test_case_insensitive():
    add_tag("ci", "Analytics")
    assert "analytics" in get_tags("ci")
