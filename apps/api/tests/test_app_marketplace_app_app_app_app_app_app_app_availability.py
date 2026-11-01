from app.services.app_marketplace_app_app_app_app_app_app_app_availability import serial_availability, parallel_availability

def test_serial():
    r = serial_availability([99.9, 99.9, 99.9])
    assert r["composite_pct"] < 99.9  # serial reduces availability
    assert r["nines"] > 2

def test_parallel():
    r = parallel_availability([99.0, 99.0])
    assert r["composite_pct"] > 99.9  # parallel increases availability
    assert r["improvement"] > 0
