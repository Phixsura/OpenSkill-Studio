from app.services.app_marketplace_app_app_app_app_app_app_app_util_heatmap import generate_heatmap

def test_heatmap():
    r = generate_heatmap([
        {"name": "n1", "cpu_pct": 30, "memory_pct": 40},
        {"name": "n2", "cpu_pct": 85, "memory_pct": 70},
        {"name": "n3", "cpu_pct": 95, "memory_pct": 90},
    ])
    assert r["hot_nodes"] == 2
    assert r["cells"][0]["color"] == "green"
    assert r["cells"][2]["color"] == "red"
