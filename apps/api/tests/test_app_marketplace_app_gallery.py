from app.services.app_marketplace_app_gallery import build_gallery, get_sort_options, get_view_modes

def test_gallery():
    apps = [{"name": "B", "install_count": 100}, {"name": "A", "install_count": 500}]
    g = build_gallery(apps=apps, view_mode="grid", sort_by="popular")
    assert g["apps"][0]["name"] == "A"  # most popular first
    assert g["columns"] == 4

def test_list_mode():
    g = build_gallery(apps=[], view_mode="list")
    assert g["columns"] == 1

def test_pagination():
    apps = [{"name": f"App{i}", "install_count": i} for i in range(50)]
    g = build_gallery(apps=apps, page=2, per_page=20)
    assert len(g["apps"]) == 20
    assert g["total_pages"] == 3

def test_sort_options():
    assert len(get_sort_options()) == 4

def test_view_modes():
    assert len(get_view_modes()) == 2
