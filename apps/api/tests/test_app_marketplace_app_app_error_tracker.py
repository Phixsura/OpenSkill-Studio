from app.services.app_marketplace_app_app_error_tracker import track_error, group_errors

def test_track():
    r = track_error(message="TypeError: undefined", source="app.js", user_id="u1")
    assert len(r["fingerprint"]) == 12
    assert r["message"] == "TypeError: undefined"

def test_group():
    e1 = track_error(message="Error A", source="x.js", user_id="u1")
    e2 = track_error(message="Error A", source="x.js", user_id="u2")
    e3 = track_error(message="Error B", source="y.js")
    r = group_errors(errors=[e1, e2, e3])
    assert r["unique_errors"] == 2
    assert r["total_errors"] == 3
    assert r["groups"][0]["count"] == 2
    assert r["groups"][0]["affected_users"] == 2
