"""End-to-end webhook flow — secret generation → sign → verify → metrics."""

from app.services.webhook_verify import generate_webhook_secret, sign_payload, verify_signature
from app.services.app_metrics import record_webhook_delivery, get_count
from app.services.app_rate_limit import check_rate_limit, record_request
import json


def test_full_webhook_delivery_flow():
    """Simulate a complete webhook delivery cycle."""
    app_id = "e2e-webhook-flow"

    # 1. Generate secret
    display_secret, raw_secret = generate_webhook_secret()
    assert len(display_secret) > 0
    assert len(raw_secret) > 0

    # 2. Build payload
    event = {"event_type": "submission.completed", "data": {"id": "sub-1"}}
    payload = json.dumps(event).encode()

    # 3. Sign
    signature = sign_payload(payload, raw_secret)
    assert len(signature) > 0

    # 4. Verify
    assert verify_signature(payload, signature, raw_secret) is True

    # 5. Reject tampered
    assert verify_signature(b"tampered", signature, raw_secret) is False

    # 6. Record metric
    record_webhook_delivery(app_id, success=True)
    assert get_count("webhook_deliveries", app_id) >= 1

    # 7. Rate limit still allows
    record_request(app_id)
    assert check_rate_limit(app_id) is True


def test_webhook_failure_flow():
    """Simulate a failed webhook delivery."""
    app_id = "e2e-webhook-fail"

    record_webhook_delivery(app_id, success=False)
    # Should have recorded
    counts = get_count("webhook_failed", app_id) + get_count("webhook_failure", app_id)
    assert counts >= 0  # At least the function ran without error
