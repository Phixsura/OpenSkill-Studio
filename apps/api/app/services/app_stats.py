"""App stats aggregator — compute aggregate statistics for apps."""


def compute_app_stats(
    *,
    installs: int = 0,
    uninstalls: int = 0,
    executions: int = 0,
    errors: int = 0,
    webhooks_sent: int = 0,
    webhooks_failed: int = 0,
    api_calls: int = 0,
) -> dict:
    """Compute aggregate stats for an app dashboard."""
    net_installs = installs - uninstalls
    exec_success_rate = ((executions - errors) / executions * 100) if executions > 0 else 100.0
    webhook_success_rate = ((webhooks_sent - webhooks_failed) / webhooks_sent * 100) if webhooks_sent > 0 else 100.0

    return {
        "total_installs": installs,
        "active_installs": max(0, net_installs),
        "total_executions": executions,
        "execution_success_rate": round(exec_success_rate, 1),
        "total_webhooks": webhooks_sent,
        "webhook_success_rate": round(webhook_success_rate, 1),
        "total_api_calls": api_calls,
        "error_count": errors,
    }
