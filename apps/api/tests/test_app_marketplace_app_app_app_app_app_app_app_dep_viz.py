from app.services.app_marketplace_app_app_app_app_app_app_app_dep_viz import to_mermaid, graph_metrics

def test_mermaid():
    r = to_mermaid(["api", "db"], [
        {"source": "api", "destination": "db", "label": "SQL"},
        {"source": "api", "destination": "cache"},
    ])
    assert "graph LR" in r
    assert "api -->|SQL| db" in r
    assert "api --> cache" in r

def test_metrics():
    r = graph_metrics(["api", "db", "cache", "web"],
                       [{"source": "web", "destination": "api"},
                        {"source": "api", "destination": "db"},
                        {"source": "api", "destination": "cache"}])
    assert r["most_dependent"] == "api"
    assert r["most_depended_on"] in ("api", "db", "cache")
    assert r["density"] > 0
