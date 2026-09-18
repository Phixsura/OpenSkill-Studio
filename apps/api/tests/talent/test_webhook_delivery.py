"""Webhook delivery tests — pure logic, no DB needed."""

from datetime import UTC, datetime

from app.talent.services.webhook_delivery import (
    MAX_RETRIES,
    RETRY_DELAYS_SECONDS,
    SUPPORTED_EVENTS,
    WebhookDelivery,
    WebhookDeliveryService,
    WebhookEndpoint,
)

svc = WebhookDeliveryService()


def _endpoint(**kw) -> WebhookEndpoint:
    defaults = {
        "id": "e1", "org_id": "o1", "url": "https://example.com/webhook",
        "secret": "test-secret-key", "event_types": [],
        "active": True, "created_at": datetime.now(UTC),
    }
    defaults.update(kw)
    return WebhookEndpoint(**defaults)


class TestConstants:
    def test_supported_events(self):
        assert "credential.issued" in SUPPORTED_EVENTS
        assert "application.submitted" in SUPPORTED_EVENTS
        assert "placement.started" in SUPPORTED_EVENTS
        assert len(SUPPORTED_EVENTS) >= 20

    def test_retry_config(self):
        assert MAX_RETRIES == 3
        assert len(RETRY_DELAYS_SECONDS) == 3
        assert RETRY_DELAYS_SECONDS[0] < RETRY_DELAYS_SECONDS[1] < RETRY_DELAYS_SECONDS[2]


class TestSignPayload:
    def test_deterministic(self):
        sig1 = svc.sign_payload('{"test": 1}', "secret")
        sig2 = svc.sign_payload('{"test": 1}', "secret")
        assert sig1 == sig2

    def test_different_payload(self):
        sig1 = svc.sign_payload('{"a": 1}', "secret")
        sig2 = svc.sign_payload('{"b": 2}', "secret")
        assert sig1 != sig2

    def test_different_secret(self):
        sig1 = svc.sign_payload('{"test": 1}', "secret1")
        sig2 = svc.sign_payload('{"test": 1}', "secret2")
        assert sig1 != sig2


class TestVerifySignature:
    def test_valid_signature(self):
        payload = '{"event": "test"}'
        sig = svc.sign_payload(payload, "my-secret")
        assert svc.verify_signature(payload, sig, "my-secret") is True

    def test_invalid_signature(self):
        assert svc.verify_signature('{"event": "test"}', "invalid", "secret") is False

    def test_wrong_secret(self):
        payload = '{"event": "test"}'
        sig = svc.sign_payload(payload, "correct-secret")
        assert svc.verify_signature(payload, sig, "wrong-secret") is False


class TestShouldDeliver:
    def test_active_no_filter(self):
        ep = _endpoint(event_types=[], active=True)
        assert svc.should_deliver(ep, "credential.issued") is True

    def test_active_matching_filter(self):
        ep = _endpoint(event_types=["credential.issued", "application.submitted"])
        assert svc.should_deliver(ep, "credential.issued") is True

    def test_active_non_matching_filter(self):
        ep = _endpoint(event_types=["credential.issued"])
        assert svc.should_deliver(ep, "application.submitted") is False

    def test_inactive(self):
        ep = _endpoint(active=False)
        assert svc.should_deliver(ep, "credential.issued") is False


class TestBuildPayload:
    def test_structure(self):
        p = svc.build_delivery_payload(
            event_type="credential.issued",
            payload={"credential_id": "c1"},
            delivery_id="d1",
        )
        assert p["event"] == "credential.issued"
        assert p["delivery_id"] == "d1"
        assert p["data"]["credential_id"] == "c1"
        assert "timestamp" in p


class TestRetryDelay:
    def test_first_retry(self):
        assert svc.get_retry_delay(0) == 10

    def test_second_retry(self):
        assert svc.get_retry_delay(1) == 60

    def test_third_retry(self):
        assert svc.get_retry_delay(2) == 300

    def test_beyond_max(self):
        assert svc.get_retry_delay(3) is None
        assert svc.get_retry_delay(10) is None


class TestStats:
    def test_empty(self):
        s = svc.compute_stats([])
        assert s.total_deliveries == 0
        assert s.success_rate == 0.0

    def test_mixed_results(self):
        now = datetime.now(UTC)
        deliveries = [
            WebhookDelivery("d1", "e1", "ev", {}, "delivered", 200, "", 1, None, now, now),
            WebhookDelivery("d2", "e1", "ev", {}, "delivered", 200, "", 1, None, now, now),
            WebhookDelivery("d3", "e1", "ev", {}, "failed", 500, "", 3, None, now, None),
            WebhookDelivery("d4", "e1", "ev", {}, "pending", None, None, 0, now, now, None),
        ]
        s = svc.compute_stats(deliveries)
        assert s.total_deliveries == 4
        assert s.successful == 2
        assert s.failed == 1
        assert s.pending == 1
        assert s.success_rate == 0.5
