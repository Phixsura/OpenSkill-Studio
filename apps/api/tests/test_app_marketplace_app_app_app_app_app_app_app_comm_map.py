from app.services.app_marketplace_app_app_app_app_app_app_app_comm_map import build_comm_map, find_chatty_services

def test_map():
    r = build_comm_map([
        {"source": "api", "destination": "db", "protocol": "tcp", "rps": 500},
        {"source": "api", "destination": "cache", "protocol": "tcp", "rps": 1000},
        {"source": "web", "destination": "api", "protocol": "http", "rps": 300},
    ])
    assert r["node_count"] == 4
    assert r["edge_count"] == 3
    assert r["total_rps"] == 1800

def test_chatty():
    cm = build_comm_map([
        {"source": "a", "destination": "b", "rps": 500},
        {"source": "c", "destination": "d", "rps": 50},
    ])
    chatty = find_chatty_services(cm, 100)
    assert len(chatty) == 1
    assert chatty[0]["source"] == "a"
