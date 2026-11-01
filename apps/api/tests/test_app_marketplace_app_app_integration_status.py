from app.services.app_marketplace_app_app_integration_status import get_integration_status

def test_status():
    r = get_integration_status(connected=["github", "slack"])
    assert r["connected"] == 2
    assert r["available"] == 4
    gh = next(i for i in r["integrations"] if i["id"] == "github")
    assert gh["connected"]
    stripe = next(i for i in r["integrations"] if i["id"] == "stripe")
    assert not stripe["connected"]
