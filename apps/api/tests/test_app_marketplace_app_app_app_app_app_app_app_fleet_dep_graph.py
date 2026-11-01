from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dep_graph import fleet_dep_graph
def test_graph():
    r = fleet_dep_graph([{"from": "A", "to": "B"}, {"from": "A", "to": "C"}, {"from": "B", "to": "D"}])
    assert r["nodes"] == 4
    assert r["edges"] == 3
    assert r["roots"] == 1
    assert r["leaves"] == 2
