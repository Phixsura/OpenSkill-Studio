from app.services.app_marketplace_app_filter_options import build_filter_options

def test_options():
    apps = [{"category": "connector", "developer_name": "Dev A"}, {"category": "automation", "developer_name": "Dev B"}]
    o = build_filter_options(apps)
    assert "connector" in o["categories"]
    assert len(o["sort_options"]) == 5
