"""Consumer API Anomaly Detector — statistical anomaly detection with alerting."""
from __future__ import annotations

import statistics
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class MetricSample:
    metric_name: str
    value: float
    timestamp: str = ""


@dataclass
class Anomaly:
    metric_name: str
    value: float
    z_score: float
    anomaly_type: str  # spike, dip, shift
    timestamp: str = ""
    severity: str = "medium"


@dataclass
class AnomalyDetector:
    """Detect statistical anomalies in API metrics."""

    _samples: dict[str, list[float]] = field(default_factory=dict)
    _anomalies: list[Anomaly] = field(default_factory=list)
    _thresholds: dict[str, float] = field(default_factory=dict)  # metric -> z-score threshold
    _default_threshold: float = 2.5

    def configure_threshold(self, metric_name: str, z_threshold: float) -> dict:
        if z_threshold <= 0:
            raise ValueError("Threshold must be positive")
        self._thresholds[metric_name] = z_threshold
        return {"metric_name": metric_name, "z_threshold": z_threshold}

    def record(self, sample: MetricSample) -> dict:
        self._samples.setdefault(sample.metric_name, []).append(sample.value)
        return {"metric_name": sample.metric_name,
                "total_samples": len(self._samples[sample.metric_name])}

    def detect(self, metric_name: str, value: float, timestamp: str = "") -> dict:
        samples = self._samples.get(metric_name, [])
        if len(samples) < 5:
            self._samples.setdefault(metric_name, []).append(value)
            return {"anomaly": False, "reason": "insufficient_data"}

        mean = statistics.mean(samples)
        stdev = statistics.stdev(samples)
        if stdev == 0:
            self._samples[metric_name].append(value)
            if value != mean:
                return {"anomaly": True, "type": "shift", "value": value}
            return {"anomaly": False}

        z_score = (value - mean) / stdev
        threshold = self._thresholds.get(metric_name, self._default_threshold)

        if abs(z_score) > threshold:
            anomaly_type = "spike" if z_score > 0 else "dip"
            severity = "critical" if abs(z_score) > threshold * 2 else "high" if abs(z_score) > threshold * 1.5 else "medium"
            anomaly = Anomaly(
                metric_name=metric_name, value=value,
                z_score=round(z_score, 2), anomaly_type=anomaly_type,
                timestamp=timestamp, severity=severity,
            )
            self._anomalies.append(anomaly)
            logger.warning("anomaly_detected", metric=metric_name, z_score=round(z_score, 2))
            self._samples[metric_name].append(value)
            return {"anomaly": True, "type": anomaly_type, "z_score": round(z_score, 2),
                    "severity": severity, "mean": round(mean, 2), "stdev": round(stdev, 2)}

        self._samples[metric_name].append(value)
        return {"anomaly": False, "z_score": round(z_score, 2)}

    def get_anomalies(self, metric_name: str | None = None, limit: int = 20) -> list[dict]:
        anomalies = self._anomalies
        if metric_name:
            anomalies = [a for a in anomalies if a.metric_name == metric_name]
        return [
            {"metric": a.metric_name, "value": a.value, "z_score": a.z_score,
             "type": a.anomaly_type, "severity": a.severity}
            for a in reversed(anomalies[-limit:])
        ]

    def get_baseline(self, metric_name: str) -> dict:
        samples = self._samples.get(metric_name, [])
        if len(samples) < 2:
            return {"metric_name": metric_name, "status": "insufficient_data"}
        return {
            "metric_name": metric_name,
            "mean": round(statistics.mean(samples), 2),
            "stdev": round(statistics.stdev(samples), 2),
            "min": min(samples),
            "max": max(samples),
            "sample_count": len(samples),
        }

    def get_stats(self) -> dict:
        return {
            "metrics_tracked": len(self._samples),
            "total_samples": sum(len(v) for v in self._samples.values()),
            "total_anomalies": len(self._anomalies),
            "by_severity": {
                s: sum(1 for a in self._anomalies if a.severity == s)
                for s in ("critical", "high", "medium")
            },
        }
