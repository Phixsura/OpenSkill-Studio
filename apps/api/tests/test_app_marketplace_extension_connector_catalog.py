from app.services.app_marketplace_extension_connector_catalog import ConnectorCatalogService

def test_register_and_browse():
    svc = ConnectorCatalogService()
    svc.register("slack", "Slack", "Slack Inc", "communication", icon="💬")
    svc.register("stripe", "Stripe", "Stripe Inc", "payment", icon="💳")
    assert len(svc.browse()) == 2
    assert len(svc.browse(category="payment")) == 1

def test_search():
    svc = ConnectorCatalogService()
    svc.register("gh", "GitHub", "GitHub Inc", "dev")
    results = svc.browse(query="git")
    assert len(results) == 1

def test_categories():
    svc = ConnectorCatalogService()
    svc.register("s1", "S3", "AWS", "storage")
    svc.register("s2", "GCS", "Google", "storage")
    svc.register("c1", "Slack", "Slack", "communication")
    cats = svc.get_categories()
    assert cats["storage"] == 2
    assert cats["communication"] == 1
