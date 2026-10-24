from app.services.app_marketplace_app_detail_page_builder import build_detail_page

def test_page():
    p = build_detail_page(app={"name": "X", "category": "connector"}, developer={"name": "D"},
        versions=[{"version": "2.0"}], stats={"installs": 100}, health={"score": 95},
        badges=[{"label": "Popular"}], reviews={"average": 4.5}, related=[{"name": "Y"}])
    assert p["latest_version"]["version"] == "2.0"
    assert len(p["breadcrumbs"]) == 3
    assert p["badges"][0]["label"] == "Popular"

def test_no_versions():
    p = build_detail_page(app={"name": "X"}, developer={}, versions=[], stats={}, health={}, badges=[], reviews={}, related=[])
    assert p["latest_version"] is None
