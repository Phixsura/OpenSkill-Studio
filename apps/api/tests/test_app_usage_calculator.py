from app.services.app_usage_calculator import compute_usage_report, estimate_cost

def test_report():
    r = compute_usage_report(executions=1000, webhook_deliveries=500, api_calls=5000, storage_bytes=10_485_760)
    assert r["total_operations"] == 6500
    assert r["storage_mb"] == 10.0

def test_report_zero():
    r = compute_usage_report(executions=0, webhook_deliveries=0, api_calls=0)
    assert r["total_operations"] == 0

def test_estimate():
    usage = compute_usage_report(executions=1000, webhook_deliveries=500, api_calls=5000)
    cost = estimate_cost(usage)
    assert cost["estimated_cost_usd"] > 0

def test_estimate_zero():
    usage = compute_usage_report(executions=0, webhook_deliveries=0, api_calls=0)
    cost = estimate_cost(usage)
    assert cost["estimated_cost_usd"] == 0

def test_custom_rates():
    usage = compute_usage_report(executions=100, webhook_deliveries=0, api_calls=0)
    cost = estimate_cost(usage, rates={"execution": 0.01, "webhook": 0, "api_call": 0, "storage_mb": 0, "bandwidth_mb": 0})
    assert cost["estimated_cost_usd"] == 1.0
