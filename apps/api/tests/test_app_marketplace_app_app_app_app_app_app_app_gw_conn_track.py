from app.services.app_marketplace_app_app_app_app_app_app_app_gw_conn_track import track_connections

def test_track():
    r = track_connections([
        {"client_ip": "1.1.1.1", "protocol": "HTTP/2", "state": "active"},
        {"client_ip": "1.1.1.1", "protocol": "HTTP/2", "state": "active"},
        {"client_ip": "2.2.2.2", "protocol": "HTTP/1.1", "state": "active"},
        {"client_ip": "3.3.3.3", "protocol": "HTTP/2", "state": "closed"},
    ])
    assert r["active"] == 3
    assert r["unique_clients"] == 2
    assert r["by_protocol"]["HTTP/2"] == 2
    assert r["top_clients"][0]["ip"] == "1.1.1.1"
