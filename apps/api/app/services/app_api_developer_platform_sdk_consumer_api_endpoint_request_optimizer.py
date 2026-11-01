"""Consumer API Endpoint Request Optimizer — optimize request patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class OptimizationSuggestion:
    suggestion_id: str
    endpoint_path: str
    category: str  # "caching", "batching", "pagination", "compression", "reduction"
    title: str
    description: str
    estimated_improvement_pct: float

@dataclass
class OptimizationReport:
    total_suggestions: int
    estimated_savings_pct: float
    suggestions: list[OptimizationSuggestion]

class AppAPIDeveloperPlatformSDKConsumerApiEndpointRequestOptimizer:
    def __init__(self) -> None:
        self._suggestions: dict[tuple[str, str], list[OptimizationSuggestion]] = {}

    def analyze(self, installation_id: str, consumer_id: str, avg_request_size_bytes: int, avg_response_size_bytes: int, cache_hit_rate_pct: float, requests_per_minute: float, unique_endpoints: int) -> OptimizationReport:
        if not installation_id:
            raise ValueError("installation_id is required")
        suggestions: list[OptimizationSuggestion] = []
        if cache_hit_rate_pct < 50:
            suggestions.append(OptimizationSuggestion(suggestion_id="s1", endpoint_path="*", category="caching", title="Enable Response Caching", description=f"Cache hit rate is only {cache_hit_rate_pct}%. Enable caching for GET endpoints.", estimated_improvement_pct=min(30, 50 - cache_hit_rate_pct)))
        if avg_response_size_bytes > 10000:
            suggestions.append(OptimizationSuggestion(suggestion_id="s2", endpoint_path="*", category="compression", title="Enable Compression", description=f"Avg response is {avg_response_size_bytes} bytes. Enable gzip compression.", estimated_improvement_pct=20))
        if requests_per_minute > 100 and unique_endpoints < 5:
            suggestions.append(OptimizationSuggestion(suggestion_id="s3", endpoint_path="*", category="batching", title="Use Batch Requests", description=f"{requests_per_minute} rpm to only {unique_endpoints} endpoints. Consider batching.", estimated_improvement_pct=25))
        if avg_request_size_bytes > 5000:
            suggestions.append(OptimizationSuggestion(suggestion_id="s4", endpoint_path="*", category="reduction", title="Reduce Request Size", description=f"Avg request is {avg_request_size_bytes} bytes. Send only needed fields.", estimated_improvement_pct=15))
        total_savings = min(60, sum(s.estimated_improvement_pct for s in suggestions))
        key = (installation_id, consumer_id)
        self._suggestions[key] = suggestions
        return OptimizationReport(total_suggestions=len(suggestions), estimated_savings_pct=round(total_savings, 1), suggestions=suggestions)

    def get_suggestions(self, installation_id: str, consumer_id: str) -> list[OptimizationSuggestion]:
        return self._suggestions.get((installation_id, consumer_id), [])
