"""Payment webhook handler — process payment provider webhooks."""
from __future__ import annotations
import hmac
import hashlib
import html


EVENTS = {"payment.completed", "payment.failed", "refund.created",
           "subscription.created", "subscription.cancelled"}


def verify_webhook(payload: str, signature: str, secret: str) -> dict:
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    valid = hmac.compare_digest(signature, expected)
    return {"valid": valid, "error": "" if valid else "signature_mismatch"}


def process_event(event_type: str, data: dict) -> dict:
    if event_type not in EVENTS:
        return {"processed": False, "error": "unknown_event"}
    amount = data.get("amount", 0)
    currency = data.get("currency", "USD")
    return {"processed": True, "event": event_type,
            "amount": amount, "currency": currency,
            "customer": html.escape(data.get("customer", "")),
            "action": _event_action(event_type)}


def _event_action(event_type: str) -> str:
    actions = {"payment.completed": "activate_subscription",
               "payment.failed": "notify_customer", "refund.created": "process_refund",
               "subscription.created": "provision_access",
               "subscription.cancelled": "revoke_access"}
    return actions.get(event_type, "log")
