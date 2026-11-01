from app.services.app_marketplace_app_app_app_app_app_app_app_incident_timer import track_incident_times, response_time_report

def test_track():
    r = track_incident_times({"detected_at": 1000, "acknowledged_at": 1300,
                               "communicated_at": 1600, "resolved_at": 2800,
                               "ack_sla_minutes": 15, "severity": "P1"})
    assert r["time_to_ack_minutes"] == 5.0
    assert r["time_to_resolve_minutes"] == 30.0
    assert r["ack_sla_met"]

def test_report():
    incidents = [
        track_incident_times({"detected_at": 100, "acknowledged_at": 400, "resolved_at": 1900, "ack_sla_minutes": 15}),
        track_incident_times({"detected_at": 200, "acknowledged_at": 1400, "resolved_at": 3800, "ack_sla_minutes": 15}),
    ]
    r = response_time_report(incidents)
    assert r["total_incidents"] == 2
    assert r["ack_sla_met"] == 1
    assert r["ack_sla_pct"] == 50.0
