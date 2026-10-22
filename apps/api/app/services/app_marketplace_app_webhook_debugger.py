"""Webhook debugger — replay, inspect, and diagnose webhook delivery issues."""

from datetime import datetime, timezone


def capture_delivery_attempt(*, webhook_id: str, event_type: str, url: str,
                                payload_size: int, response: dict) -> dict:
    return {
        "webhook_id": webhook_id, "event_type": event_type, "url": url,
        "payload_size": payload_size, "status_code": response.get("status_code", 0),
        "response_body_preview": (response.get("body", "") or "")[:200],
        "response_time_ms": response.get("duration_ms", 0),
        "success": 200 <= response.get("status_code", 0) < 300,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def diagnose_failure(*, attempt: dict) -> dict:
    code = attempt.get("status_code", 0)
    diagnosis = {"cause": "unknown", "suggestion": "Check endpoint logs"}
    if code == 0:
        diagnosis = {"cause": "connection_failed", "suggestion": "Verify URL is reachable and accepts HTTPS"}
    elif code == 401:
        diagnosis = {"cause": "authentication", "suggestion": "Check webhook secret configuration"}
    elif code == 404:
        diagnosis = {"cause": "endpoint_not_found", "suggestion": "Verify webhook URL path is correct"}
    elif code == 429:
        diagnosis = {"cause": "rate_limited", "suggestion": "Reduce event frequency or increase rate limits"}
    elif code >= 500:
        diagnosis = {"cause": "server_error", "suggestion": "Check your server logs for errors"}
    elif attempt.get("response_time_ms", 0) > 10000:
        diagnosis = {"cause": "timeout", "suggestion": "Optimize handler to respond within 10 seconds"}
    return {**diagnosis, "status_code": code}


def build_replay_request(*, original: dict) -> dict:
    return {"url": original["url"], "method": "POST",
            "headers": {"Content-Type": "application/json", "X-Replay": "true"},
            "event_type": original["event_type"]}
