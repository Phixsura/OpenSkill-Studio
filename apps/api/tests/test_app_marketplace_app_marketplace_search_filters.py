from app.services.app_marketplace_app_marketplace_search_filters import get_filter_definitions, apply_filters, compute_filter_counts

def test_definitions():
    d = get_filter_definitions()
    assert "category" in d
    assert "rating" in d
    assert len(d) >= 6

def test_filter_category():
    apps = [{"name": "A", "category": "connector"}, {"name": "B", "category": "analytics"}]
    r = apply_filters(apps=apps, filters={"category": "connector"})
    assert len(r) == 1

def test_filter_rating():
    apps = [{"name": "A", "avg_rating": 4.5}, {"name": "B", "avg_rating": 3.0}]
    r = apply_filters(apps=apps, filters={"rating": 4})
    assert len(r) == 1

def test_sort_installs():
    apps = [{"name": "A", "install_count": 10}, {"name": "B", "install_count": 100}]
    r = apply_filters(apps=apps, filters={"sort": "installs"})
    assert r[0]["name"] == "B"

def test_counts():
    apps = [{"category": "connector", "price_cents": 0}, {"category": "connector", "price_cents": 999},
            {"category": "analytics", "price_cents": 0}]
    c = compute_filter_counts(apps=apps)
    assert c["category"]["connector"] == 2
    assert c["pricing"]["free"] == 2
