from app.services.app_marketplace_app_app_app_app_app_app_app_otel_exporter import OtelExporter

def test_exporter():
    exp = OtelExporter(batch_size=3)
    exp.add_span(service="api", operation="GET /users", duration_ms=50)
    exp.add_span(service="api", operation="POST /users", duration_ms=120)
    assert exp.stats()["buffered"] == 2
    r = exp.add_span(service="db", operation="SELECT", duration_ms=15)
    assert r["flushed"]  # batch_size reached
    assert exp.stats()["exported"] == 3
    assert exp.stats()["batches_sent"] == 1
    exp.add_span(service="cache", operation="GET", duration_ms=2)
    exp.flush()
    assert exp.stats()["exported"] == 4
