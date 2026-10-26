from app.services.app_marketplace_extension_telemetry_pipeline import (
    TelemetryPipelineService, TelemetryType, ExportTarget,
)
import pytest


def test_configure_and_ingest():
    svc = TelemetryPipelineService()
    svc.configure("ext-1", export_targets=[ExportTarget.PROMETHEUS])
    record = svc.ingest("ext-1", TelemetryType.METRIC, "request_count", 1)
    assert record is not None
    assert record.name == "request_count"


def test_sampling():
    svc = TelemetryPipelineService()
    svc.configure("ext-1", sampling_rate=0.0)  # drop all
    record = svc.ingest("ext-1", TelemetryType.METRIC, "test", 1)
    assert record is None
    stats = svc.get_stats()
    assert stats["dropped_by_sampling"] == 1


def test_full_sampling():
    svc = TelemetryPipelineService()
    svc.configure("ext-1", sampling_rate=1.0)
    for i in range(10):
        svc.ingest("ext-1", TelemetryType.METRIC, "counter", i)
    results = svc.query("ext-1")
    assert len(results) == 10


def test_query_filter():
    svc = TelemetryPipelineService()
    svc.configure("ext-1")
    svc.ingest("ext-1", TelemetryType.METRIC, "cpu", 50)
    svc.ingest("ext-1", TelemetryType.LOG, "error", 1)
    svc.ingest("ext-1", TelemetryType.METRIC, "memory", 80)
    results = svc.query("ext-1", telemetry_type=TelemetryType.METRIC)
    assert len(results) == 2


def test_aggregate():
    svc = TelemetryPipelineService()
    svc.configure("ext-1")
    for v in [10, 20, 30, 40, 50]:
        svc.ingest("ext-1", TelemetryType.METRIC, "latency", v)
    agg = svc.aggregate("ext-1", "latency")
    assert agg["count"] == 5
    assert agg["avg"] == 30.0
    assert agg["min"] == 10
    assert agg["max"] == 50


def test_export_tracking():
    svc = TelemetryPipelineService()
    svc.configure("ext-1", export_targets=[ExportTarget.DATADOG, ExportTarget.PROMETHEUS])
    svc.ingest("ext-1", TelemetryType.EVENT, "deploy")
    stats = svc.get_stats()
    assert stats["exported"]["datadog"] == 1
    assert stats["exported"]["prometheus"] == 1


def test_invalid_sampling():
    svc = TelemetryPipelineService()
    with pytest.raises(ValueError):
        svc.configure("ext-1", sampling_rate=1.5)


def test_flush():
    svc = TelemetryPipelineService()
    svc.configure("ext-1")
    svc.ingest("ext-1", TelemetryType.METRIC, "a", 1)
    svc.ingest("ext-1", TelemetryType.METRIC, "b", 2)
    flushed = svc.flush("ext-1")
    assert flushed == 2
    assert len(svc.query("ext-1")) == 0
