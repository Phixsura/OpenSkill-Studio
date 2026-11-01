from app.services.app_marketplace_app_developer_app_log_exporter import create_export_config, format_log_batch, get_export_stats

def test_create():
    c = create_export_config(destination="datadog", endpoint_url="https://intake.datadoghq.com", api_key="key123")
    assert c["status"] == "configured"
    assert c["format"] == "json"

def test_invalid_dest():
    c = create_export_config(destination="prometheus", endpoint_url="x", api_key="y")
    assert c["error"]

def test_format_json():
    logs = [{"level": "info", "message": "test"}]
    r = format_log_batch(logs=logs, format="json")
    assert '"level"' in r[0]

def test_format_logfmt():
    logs = [{"level": "info", "msg": "test"}]
    r = format_log_batch(logs=logs, format="logfmt")
    assert 'level="info"' in r[0]

def test_stats():
    exports = [{"log_count": 1000, "status": "success"}, {"log_count": 500, "status": "failed"}]
    s = get_export_stats(exports=exports)
    assert s["total_logs"] == 1500
    assert s["success_rate"] == 50.0
