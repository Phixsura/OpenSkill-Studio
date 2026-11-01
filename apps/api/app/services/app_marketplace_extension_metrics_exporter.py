"""Metrics Exporter — export extension metrics in Prometheus/OpenMetrics format.

Collects counters, gauges, histograms and exports them in text-based
exposition format for monitoring system ingestion.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import math


class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class Metric:
    name: str
    metric_type: MetricType
    help_text: str
    labels: dict[str, str] = field(default_factory=dict)


class MetricsExporterService:
    """Collects and exports metrics in Prometheus exposition format."""

    def __init__(self):
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._help: dict[str, str] = {}
        self._types: dict[str, MetricType] = {}

    def register(self, name: str, metric_type: MetricType,
                 help_text: str = "") -> None:
        if not name.replace("_", "").replace(":", "").isalnum():
            raise ValueError(f"Invalid metric name: {name}")
        self._help[name] = help_text
        self._types[name] = metric_type

    def inc(self, name: str, value: float = 1.0,
            labels: dict[str, str] | None = None) -> float:
        if self._types.get(name) != MetricType.COUNTER:
            raise ValueError(f"{name} is not a counter")
        if value < 0:
            raise ValueError("Counter can only increase")
        key = self._label_key(name, labels)
        self._counters[key] += value
        return self._counters[key]

    def set_gauge(self, name: str, value: float,
                  labels: dict[str, str] | None = None) -> None:
        if self._types.get(name) != MetricType.GAUGE:
            raise ValueError(f"{name} is not a gauge")
        key = self._label_key(name, labels)
        self._gauges[key] = value

    def observe(self, name: str, value: float,
                labels: dict[str, str] | None = None) -> None:
        if self._types.get(name) != MetricType.HISTOGRAM:
            raise ValueError(f"{name} is not a histogram")
        key = self._label_key(name, labels)
        self._histograms[key].append(value)

    def _label_key(self, name: str, labels: dict[str, str] | None) -> str:
        if not labels:
            return name
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def get_counter(self, name: str, labels: dict[str, str] | None = None) -> float:
        return self._counters.get(self._label_key(name, labels), 0.0)

    def get_gauge(self, name: str, labels: dict[str, str] | None = None) -> float | None:
        return self._gauges.get(self._label_key(name, labels))

    def get_histogram_stats(self, name: str,
                            labels: dict[str, str] | None = None) -> dict:
        key = self._label_key(name, labels)
        values = self._histograms.get(key, [])
        if not values:
            return {"count": 0, "sum": 0, "avg": 0, "p50": 0, "p99": 0}
        sorted_v = sorted(values)
        return {
            "count": len(values),
            "sum": round(sum(values), 3),
            "avg": round(sum(values) / len(values), 3),
            "p50": sorted_v[len(sorted_v) // 2],
            "p99": sorted_v[int(len(sorted_v) * 0.99)],
        }

    def export_text(self) -> str:
        lines: list[str] = []
        seen_names: set[str] = set()

        for key, value in sorted(self._counters.items()):
            name = key.split("{")[0]
            if name not in seen_names:
                if name in self._help:
                    lines.append(f"# HELP {name} {self._help[name]}")
                lines.append(f"# TYPE {name} counter")
                seen_names.add(name)
            lines.append(f"{key} {value}")

        for key, value in sorted(self._gauges.items()):
            name = key.split("{")[0]
            if name not in seen_names:
                if name in self._help:
                    lines.append(f"# HELP {name} {self._help[name]}")
                lines.append(f"# TYPE {name} gauge")
                seen_names.add(name)
            lines.append(f"{key} {value}")

        return "\n".join(lines) + "\n" if lines else ""
