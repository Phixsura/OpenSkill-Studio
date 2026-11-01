from app.services.app_marketplace_app_app_app_app_app_app_app_svc_version import track_versions, version_matrix

def test_track():
    r = track_versions([
        {"service": "api", "env": "prod", "version": "2.0"},
        {"service": "api", "env": "staging", "version": "2.1"},
        {"service": "web", "env": "prod", "version": "3.0"},
        {"service": "web", "env": "staging", "version": "3.0"},
    ])
    assert not r["all_consistent"]
    assert len(r["inconsistent"]) == 1
    assert r["inconsistent"][0]["service"] == "api"

def test_matrix():
    m = version_matrix({"api": {"prod": "2.0", "staging": "2.1"}, "web": {"prod": "3.0"}}, ["prod", "staging"])
    assert m[0]["service"] == "api"
    assert m[0]["staging"] == "2.1"
    assert m[1]["staging"] == "-"
