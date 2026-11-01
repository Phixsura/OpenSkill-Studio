from app.services.app_marketplace_network_monitor import NetworkMonitor, NetworkRequest


def test_record_and_get():
    nm = NetworkMonitor()
    nm.record(NetworkRequest("r1", "ext-1", "GET", "https://api.slack.com/users", 200, 50, 1024, 45.0))
    nm.record(NetworkRequest("r2", "ext-1", "POST", "https://api.slack.com/messages", 200, 200, 512, 120.0))
    reqs = nm.get_requests("ext-1")
    assert len(reqs) == 2


def test_filter_by_method():
    nm = NetworkMonitor()
    nm.record(NetworkRequest("r1", "ext-2", "GET", "https://a.com", 200))
    nm.record(NetworkRequest("r2", "ext-2", "POST", "https://a.com", 201))
    gets = nm.get_requests("ext-2", method="GET")
    assert len(gets) == 1


def test_bandwidth():
    nm = NetworkMonitor(bandwidth_limit_mb=1.0)
    nm.record(NetworkRequest("r1", "ext-3", "GET", "https://a.com", 200, 100, 500000, 50))
    nm.record(NetworkRequest("r2", "ext-3", "GET", "https://b.com", 200, 100, 600000, 50))
    bw = nm.get_bandwidth_used("ext-3")
    assert bw["total_bytes"] == 1100200
    assert bw["exceeded"] is True


def test_top_domains():
    nm = NetworkMonitor()
    for i in range(5):
        nm.record(NetworkRequest(f"r{i}", "ext-4", "GET", "https://api.slack.com/x", 200, 10, 100, 40))
    nm.record(NetworkRequest("r10", "ext-4", "GET", "https://api.github.com/y", 200, 10, 100, 60))
    top = nm.get_top_domains("ext-4")
    assert top[0]["domain"] == "api.slack.com"
    assert top[0]["count"] == 5


def test_error_rate():
    nm = NetworkMonitor()
    nm.record(NetworkRequest("r1", "ext-5", "GET", "https://a.com", 200))
    nm.record(NetworkRequest("r2", "ext-5", "GET", "https://a.com", 500))
    nm.record(NetworkRequest("r3", "ext-5", "GET", "https://a.com", 200, blocked=True, block_reason="policy"))
    assert nm.get_error_rate("ext-5") == 66.67


def test_summary():
    nm = NetworkMonitor()
    nm.record(NetworkRequest("r1", "ext-6", "GET", "https://a.com/x", 200, 10, 100))
    nm.record(NetworkRequest("r2", "ext-6", "GET", "https://b.com/y", 200, 10, 100))
    summary = nm.get_summary("ext-6")
    assert summary["total_requests"] == 2
    assert summary["unique_domains"] == 2
