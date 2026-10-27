from app.services.app_marketplace_extension_error_classifier import ErrorClassifierService


def test_timeout():
    ec = ErrorClassifierService()
    result = ec.classify("Connection timed out after 30s")
    assert result.error_type == "transient"
    assert result.retryable is True
    assert result.category == "network"


def test_connection_refused():
    ec = ErrorClassifierService()
    result = ec.classify("Connection refused to port 5432")
    assert result.retryable is True
    assert "service is running" in result.remediation


def test_auth_failure():
    ec = ErrorClassifierService()
    result = ec.classify("401 Unauthorized: Invalid API key")
    assert result.error_type == "permanent"
    assert result.retryable is False
    assert result.category == "auth"


def test_validation_error():
    ec = ErrorClassifierService()
    result = ec.classify("400 Bad Request: Invalid email format")
    assert result.error_type == "validation"
    assert result.category == "input"


def test_oom():
    ec = ErrorClassifierService()
    result = ec.classify("Process killed: out of memory")
    assert result.severity == "critical"
    assert result.category == "system"
    assert result.retryable is False


def test_rate_limit():
    ec = ErrorClassifierService()
    result = ec.classify("429 Too Many Requests")
    assert result.retryable is True
    assert "backoff" in result.remediation.lower() or "back off" in result.remediation.lower()


def test_deadlock():
    ec = ErrorClassifierService()
    result = ec.classify("Deadlock detected in transaction")
    assert result.category == "database"
    assert result.retryable is True


def test_not_found():
    ec = ErrorClassifierService()
    result = ec.classify("404 Not Found: User does not exist")
    assert result.error_type == "permanent"
    assert result.retryable is False


def test_unknown():
    ec = ErrorClassifierService()
    result = ec.classify("Something completely novel happened")
    assert result.error_type == "unknown"
    assert result.category == "unknown"


def test_batch_classify():
    ec = ErrorClassifierService()
    errors = [
        "Connection timeout", "401 Unauthorized",
        "Connection timeout", "500 Internal Server Error",
        "Invalid input format",
    ]
    summary = ec.classify_batch(errors)
    assert summary["total"] == 5
    assert summary["retryable_pct"] > 0
    assert "transient" in summary["by_type"]


def test_top_errors():
    ec = ErrorClassifierService()
    for _ in range(5):
        ec.classify("Connection timeout")
    for _ in range(3):
        ec.classify("401 Unauthorized")
    top = ec.get_top_errors(2)
    assert len(top) == 2
    assert top[0][1] >= top[1][1]
