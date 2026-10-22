import json
from app.services.app_data_export import export_app_data

def test_basic():
    result = json.loads(export_app_data({"id": "a1", "name": "App"}))
    assert result["export_version"] == "1.0"

def test_strips_secret_hash():
    result = json.loads(export_app_data({"id": "a1", "oauth_client_secret_hash": "xxx"}))
    assert "oauth_client_secret_hash" not in result["app"]

def test_with_versions():
    result = json.loads(export_app_data({"id": "a1"}, versions=[{"version": "1.0.0"}]))
    assert len(result["versions"]) == 1
