from app.services.app_marketplace_data_export_request import create_export_request, estimate_export_size, complete_export

def test_create():
    r = create_export_request(developer_id="d1", export_type="full")
    assert r["status"] == "queued"

def test_invalid_type():
    r = create_export_request(developer_id="d1", export_type="secret")
    assert r["error"]

def test_estimate():
    e = estimate_export_size(app_count=10, install_count=500, review_count=200)
    assert e["estimated_kb"] > 0

def test_complete():
    req = {"developer_id": "d1", "status": "queued"}
    r = complete_export(request=req, download_url="https://dl.example.com/export.zip", size_bytes=1024000)
    assert r["status"] == "completed"
    assert r["download_url"]
