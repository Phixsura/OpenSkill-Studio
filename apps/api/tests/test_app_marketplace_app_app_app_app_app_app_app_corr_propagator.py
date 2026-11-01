from app.services.app_marketplace_app_app_app_app_app_app_app_corr_propagator import CorrelationPropagator

def test_extract():
    cp = CorrelationPropagator()
    r = cp.extract_or_create({"X-Correlation-ID": "existing-id"})
    assert r["correlation_id"] == "existing-id"
    assert not r["created"]

def test_create():
    cp = CorrelationPropagator()
    r = cp.extract_or_create({})
    assert r["correlation_id"].startswith("corr-")
    assert r["created"]

def test_track():
    cp = CorrelationPropagator()
    cp.track_hop("c1", "gateway")
    cp.track_hop("c1", "api")
    cp.track_hop("c1", "db")
    assert cp.get_chain("c1") == ["gateway", "api", "db"]
