from app.services.app_marketplace_extension_abuse_detection import AbuseDetectionService


def test_normal_traffic():
    ads = AbuseDetectionService(rate_threshold=100)
    for _ in range(50):
        signals = ads.record_request("ext-1", "1.2.3.4")
    assert len(signals) == 0


def test_rate_spike():
    ads = AbuseDetectionService(rate_threshold=100)
    for _ in range(101):
        ads.record_request("ext-2")
    signals = ads.get_signals("ext-2", "high")
    assert any(s.signal_type == "rate_spike" for s in signals)


def test_credential_stuffing():
    ads = AbuseDetectionService()
    for _ in range(50):
        ads.record_request("ext-3", status_code=200)
    for _ in range(60):
        ads.record_request("ext-3", status_code=401)
    signals = ads.get_signals("ext-3", "critical")
    assert any(s.signal_type == "credential_stuffing" for s in signals)


def test_distributed_abuse():
    ads = AbuseDetectionService(rate_threshold=10000)
    for i in range(101):
        ads.record_request("ext-4", ip=f"10.0.0.{i % 256}")
    signals = ads.get_signals("ext-4")
    assert any(s.signal_type == "distributed_abuse" for s in signals)


def test_block_unblock():
    ads = AbuseDetectionService()
    ads.block("ext-5")
    assert ads.is_blocked("ext-5") is True
    ads.unblock("ext-5")
    assert ads.is_blocked("ext-5") is False


def test_risk_score():
    ads = AbuseDetectionService(rate_threshold=10)
    for _ in range(20):
        ads.record_request("ext-6")
    risk = ads.get_risk_score("ext-6")
    assert risk["score"] > 0
    assert risk["risk"] in ("low", "medium", "high", "critical")
