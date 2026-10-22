from app.services.app_marketplace_app_gallery import build_category_gallery, build_developer_gallery

APPS = [{"name": "B", "install_count": 50, "category": "connector", "status": "published"},
        {"name": "A", "install_count": 100, "category": "connector", "status": "published"}]

def test_category_gallery():
    g = build_category_gallery(category="connector", apps=APPS)
    assert g["total"] == 2
    assert g["apps"][0]["install_count"] == 100  # sorted by installs

def test_sort_by_name():
    g = build_category_gallery(category="connector", apps=APPS, sort_by="name")
    assert g["apps"][0]["name"] == "A"

def test_developer_gallery():
    g = build_developer_gallery(developer_name="Dev", apps=APPS)
    assert g["developer"] == "Dev"
    assert g["total"] == 2
