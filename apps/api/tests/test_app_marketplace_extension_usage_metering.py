from app.services.app_marketplace_extension_usage_metering import ExtUsageMeteringService

def test_configure_and_record():
    svc = ExtUsageMeteringService()
    svc.configure("ext-1", "u1", "api_calls", 1)  # 1 cent per call
    svc.record("ext-1", "u1", "api_calls", 100)
    bill = svc.get_bill("ext-1", "u1")
    assert bill["total_cents"] == 100

def test_multiple_metrics():
    svc = ExtUsageMeteringService()
    svc.configure("ext-1", "u1", "api_calls", 1)
    svc.configure("ext-1", "u1", "storage_mb", 5)
    svc.record("ext-1", "u1", "api_calls", 200)
    svc.record("ext-1", "u1", "storage_mb", 50)
    bill = svc.get_bill("ext-1", "u1")
    assert bill["total_cents"] == 450  # 200 + 250

def test_reset():
    svc = ExtUsageMeteringService()
    svc.configure("ext-1", "u1", "api_calls", 1)
    svc.record("ext-1", "u1", "api_calls", 100)
    svc.reset_period("ext-1", "u1")
    bill = svc.get_bill("ext-1", "u1")
    assert bill["total_cents"] == 0
