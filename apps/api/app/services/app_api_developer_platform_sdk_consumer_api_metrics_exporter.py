"""Consumer API Metrics Exporter — Prometheus-format metrics export."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

METRIC_TYPES = ("counter", "gauge", "histogram", "summary")


@dataclass
class MetricDefinition:
    name: str
    metric_type: str
    help_text: str = ""
    labels: list[str] = field(default_factory=list)


@dataclass
class MetricValue:
    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = 0.0


@dataclass
class MetricsExporter:
    """Export API metrics in Prometheus text format."""

    _definitions: dict[str, MetricDefinition] = field(default_factory=dict)
    _values: dict[str, list[MetricValue]] = field(default_factory=dict)

    def define(self, definition: MetricDefinition) -> dict:
        if definition.metric_type not in METRIC_TYPES:
            raise ValueError(f"Invalid type: {definition.metric_type}")
        if definition.name in self._definitions:
            raise ValueError(f"Metric {definition.name} already defined")
        self._definitions[definition.name] = definition
        self._values[definition.name] = []
        logger.info("metric_defined", name=definition.name, type=definition.metric_type)
        return {"name": definition.name, "type": definition.metric_type}

    def record(self, name: str, value: float, labels: dict[str, str] | None = None,
               timestamp: float = 0.0) -> dict:
        if name not in self._definitions:
            raise ValueError(f"Metric {name} not defined")
        defn = self._definitions[name]
        if defn.metric_type == "counter" and value < 0:
            raise ValueError("Counter values must be non-negative")
        mv = MetricValue(name=name, value=value, labels=labels or {}, timestamp=timestamp)
        self._values[name].append(mv)
        return {"name": name, "recorded": True}

    def increment(self, name: str, amount: float = 1.0,
                  labels: dict[str, str] | None = None) -> dict:
        if name not in self._definitions:
            raise ValueError(f"Metric {name} not defined")
        if amount < 0:
            raise ValueError("Increment must be non-negative")
        # Find latest value with matching labels or start at 0
        current = 0.0
        lbl = labels or {}
        for v in reversed(self._values.get(name, [])):
            if v.labels == lbl:
                current = v.value
                break
        new_val = current + amount
        self._values[name].append(MetricValue(name=name, value=new_val, labels=lbl))
        return {"name": name, "value": new_val}

    def export_prometheus(self) -> str:
        lines = []
        for name, defn in sorted(self._definitions.items()):
            lines.append(f"# HELP {name} {defn.help_text}")
            lines.append(f"# TYPE {name} {defn.metric_type}")
            # Get latest value per label set
            latest: dict[str, MetricValue] = {}
            for v in self._values.get(name, []):
                key = str(sorted(v.labels.items()))
                latest[key] = v
            for v in latest.values():
                if v.labels:
                    label_str = ",".join(f'{k}="{val}"' for k, val in sorted(v.labels.items()))
                    lines.append(f"{name}{{{label_str}}} {v.value}")
                else:
                    lines.append(f"{name} {v.value}")
        return "\n".join(lines)

    def get_metric(self, name: str) -> dict | None:
        defn = self._definitions.get(name)
        if not defn:
            return None
        values = self._values.get(name, [])
        latest: dict[str, float] = {}
        for v in values:
            key = str(sorted(v.labels.items()))
            latest[key] = v.value
        return {
            "name": defn.name,
            "type": defn.metric_type,
            "help": defn.help_text,
            "series_count": len(latest),
            "total_samples": len(values),
        }

    def list_metrics(self) -> list[dict]:
        return [self.get_metric(n) for n in sorted(self._definitions)]

    def get_stats(self) -> dict:
        total_samples = sum(len(v) for v in self._values.values())
        return {
            "total_metrics": len(self._definitions),
            "total_samples": total_samples,
            "by_type": {t: sum(1 for d in self._definitions.values() if d.metric_type == t)
                        for t in METRIC_TYPES},
        }
