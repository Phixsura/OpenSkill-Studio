from app.services.app_marketplace_app_app_label_manager import create_label, build_label_list, auto_color

def test_create():
    r = create_label(name="bug", color="#EF4444", description="Bug reports")
    assert r["name"] == "bug"
    assert r["slug"] == "bug"

def test_auto_color():
    c = auto_color("test")
    assert c.startswith("#")

def test_invalid_name():
    r = create_label(name="!invalid")
    assert "error" in r

def test_list():
    labels = [{"name": "bug", "count": 10}, {"name": "feature", "count": 25}]
    r = build_label_list(labels=labels)
    assert r["total"] == 2
    assert r["labels"][0]["name"] == "feature"  # sorted by count desc
