"""Consumer API Usage Insight — generate actionable insights from API usage data."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class UsageInsight:
    insight_id: str
    category: str  # "optimization", "security", "cost", "performance", "adoption"
    severity: str  # "info", "warning", "critical"
    title: str
    description: str
    recommendation: str
    metric_value: float = 0.0
    threshold: float = 0.0
    generated_at: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiUsageInsight:
    def __init__(self) -> None:
        self._insights: dict[tuple[str, str], list[UsageInsight]] = {}

    def generate(self, installation_id: str, consumer_id: str, error_rate: float, avg_latency_ms: float, daily_requests: int, unused_endpoints: int, now: datetime) -> list[UsageInsight]:
        if not installation_id:
            raise ValueError("installation_id is required")
        insights: list[UsageInsight] = []
        if error_rate > 5.0:
            insights.append(UsageInsight(insight_id=f"err-{now.isoformat()}", category="performance", severity="critical", title="High Error Rate", description=f"Error rate is {error_rate}%", recommendation="Review error logs and fix failing endpoints", metric_value=error_rate, threshold=5.0, generated_at=now))
        elif error_rate > 1.0:
            insights.append(UsageInsight(insight_id=f"err-{now.isoformat()}", category="performance", severity="warning", title="Elevated Error Rate", description=f"Error rate is {error_rate}%", recommendation="Monitor error trends", metric_value=error_rate, threshold=1.0, generated_at=now))
        if avg_latency_ms > 500:
            insights.append(UsageInsight(insight_id=f"lat-{now.isoformat()}", category="performance", severity="warning", title="High Latency", description=f"Average latency is {avg_latency_ms}ms", recommendation="Consider caching or query optimization", metric_value=avg_latency_ms, threshold=500, generated_at=now))
        if daily_requests > 50000:
            insights.append(UsageInsight(insight_id=f"vol-{now.isoformat()}", category="cost", severity="info", title="High Volume", description=f"{daily_requests} daily requests", recommendation="Consider upgrading to a higher tier for better pricing", metric_value=float(daily_requests), threshold=50000, generated_at=now))
        if unused_endpoints > 5:
            insights.append(UsageInsight(insight_id=f"unused-{now.isoformat()}", category="optimization", severity="info", title="Unused Endpoints", description=f"{unused_endpoints} endpoints have no traffic", recommendation="Review and consider deprecating unused endpoints", metric_value=float(unused_endpoints), threshold=5, generated_at=now))
        key = (installation_id, consumer_id)
        self._insights[key] = insights
        return insights

    def get_insights(self, installation_id: str, consumer_id: str, category: str | None = None, severity: str | None = None) -> list[UsageInsight]:
        insights = self._insights.get((installation_id, consumer_id), [])
        if category:
            insights = [i for i in insights if i.category == category]
        if severity:
            insights = [i for i in insights if i.severity == severity]
        return sorted(insights, key=lambda i: {"critical": 0, "warning": 1, "info": 2}.get(i.severity, 3))
