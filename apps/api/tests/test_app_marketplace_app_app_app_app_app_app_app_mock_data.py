from app.services.app_marketplace_app_app_app_app_app_app_app_mock_data import generate_users, generate_orders, data_stats

def test_users():
    users = generate_users(10)
    assert len(users) == 10
    assert users[0]["id"].startswith("usr_")
    assert "@example.com" in users[0]["email"]

def test_orders():
    users = generate_users(3)
    orders = generate_orders(5, [u["id"] for u in users])
    assert len(orders) == 5
    assert orders[0]["id"].startswith("ord_")

def test_stats():
    users = generate_users(5)
    s = data_stats(users)
    assert s["count"] == 5
    assert "id" in s["fields"]
