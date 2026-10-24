from app.services.app_status_counter import count_by_status, count_by_category, count_by_visibility

APPS = [{"status": "published", "category": "connector", "visibility": "public"},
        {"status": "published", "category": "connector", "visibility": "public"},
        {"status": "draft", "category": "automation", "visibility": "private"}]

def test_by_status():
    c = count_by_status(APPS)
    assert c["published"] == 2
    assert c["draft"] == 1

def test_by_category():
    c = count_by_category(APPS)
    assert c["connector"] == 2

def test_by_visibility():
    c = count_by_visibility(APPS)
    assert c["public"] == 2
    assert c["private"] == 1
