from app.services.app_page_meta_builder import build_app_page

def test_page():
    p = build_app_page(app={"name": "X", "slug": "x"}, developer={"name": "D"}, versions=[{"version": "2.0"}], stats={}, badges=[])
    assert p["latest_version"]["version"] == "2.0"
    assert p["version_count"] == 1
    assert len(p["breadcrumbs"]) == 3
