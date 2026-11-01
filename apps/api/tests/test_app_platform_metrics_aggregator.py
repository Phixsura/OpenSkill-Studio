from app.services.app_platform_metrics_aggregator import aggregate_platform_metrics

def test_healthy():
    m = aggregate_platform_metrics(apps=100, developers=20, installations=500, executions_24h=10000,
        errors_24h=50, webhooks_24h=2000, avg_health=97, active_users_7d=150)
    assert m["health"]["status"] == "healthy"
    assert m["overview"]["apps"] == 100
    assert m["activity_24h"]["error_rate"] == 0.5

def test_critical():
    m = aggregate_platform_metrics(apps=10, developers=2, installations=5, executions_24h=100,
        errors_24h=20, webhooks_24h=10, avg_health=60, active_users_7d=3)
    assert m["health"]["status"] == "critical"

def test_zero_executions():
    m = aggregate_platform_metrics(apps=0, developers=0, installations=0, executions_24h=0,
        errors_24h=0, webhooks_24h=0, avg_health=100, active_users_7d=0)
    assert m["activity_24h"]["error_rate"] == 0
