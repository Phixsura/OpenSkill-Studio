"""Webhook test result — format test delivery results for display."""


def format_test_result(*, success: bool, status_code: int | None, duration_ms: int,
                        response_body: str | None, error: str | None) -> dict:
    return {
        "success": success,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "response_preview": (response_body or "")[:500],
        "error": error,
        "verdict": "✅ Webhook endpoint is working" if success else f"❌ {error or f'HTTP {status_code}'}",
    }
