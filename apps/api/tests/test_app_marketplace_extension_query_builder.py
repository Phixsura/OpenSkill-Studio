from app.services.app_marketplace_extension_query_builder import QueryBuilderService


def test_simple_select():
    qb = QueryBuilderService()
    q = qb.from_table("users").select("id", "name").build()
    assert q.sql == "SELECT id, name FROM users"
    assert q.params == []


def test_select_all():
    qb = QueryBuilderService()
    q = qb.from_table("users").build()
    assert q.sql == "SELECT * FROM users"


def test_where():
    qb = QueryBuilderService()
    q = (qb.from_table("users")
         .where_eq("status", "active")
         .where("age", ">=", 18)
         .build())
    assert "WHERE status = ? AND age >= ?" in q.sql
    assert q.params == ["active", 18]


def test_where_in():
    qb = QueryBuilderService()
    q = (qb.from_table("orders")
         .where_in("status", ["pending", "processing", "shipped"])
         .build())
    assert "IN (?, ?, ?)" in q.sql
    assert q.params == ["pending", "processing", "shipped"]


def test_where_between():
    qb = QueryBuilderService()
    q = (qb.from_table("events")
         .where_between("created_at", "2024-01-01", "2024-12-31")
         .build())
    assert "BETWEEN ? AND ?" in q.sql
    assert q.params == ["2024-01-01", "2024-12-31"]


def test_join():
    qb = QueryBuilderService()
    q = (qb.from_table("orders")
         .select("orders.id", "users.name")
         .join("users", "orders.user_id = users.id")
         .build())
    assert "INNER JOIN users ON orders.user_id = users.id" in q.sql


def test_left_join():
    qb = QueryBuilderService()
    q = (qb.from_table("users")
         .left_join("profiles", "users.id = profiles.user_id")
         .build())
    assert "LEFT JOIN profiles" in q.sql


def test_order_and_limit():
    qb = QueryBuilderService()
    q = (qb.from_table("posts")
         .order_by("created_at", "DESC")
         .limit(10).offset(20)
         .build())
    assert "ORDER BY created_at DESC" in q.sql
    assert "LIMIT 10" in q.sql
    assert "OFFSET 20" in q.sql


def test_group_by_having():
    qb = QueryBuilderService()
    q = (qb.from_table("orders")
         .select("user_id", "COUNT(*) as order_count")
         .group_by("user_id")
         .having("COUNT(*)", ">", 5)
         .build())
    assert "GROUP BY user_id" in q.sql
    assert "HAVING COUNT(*) > ?" in q.sql
    assert q.params == [5]


def test_count():
    qb = QueryBuilderService()
    q = (qb.from_table("users")
         .where_eq("active", True)
         .count())
    assert "COUNT(*)" in q.sql
    assert q.params == [True]


def test_complex_query():
    qb = QueryBuilderService()
    q = (qb.from_table("orders")
         .select("orders.id", "users.name", "SUM(items.price) as total")
         .join("users", "orders.user_id = users.id")
         .join("items", "orders.id = items.order_id")
         .where_eq("orders.status", "completed")
         .where("orders.created_at", ">", "2024-01-01")
         .group_by("orders.id", "users.name")
         .having("SUM(items.price)", ">", 100)
         .order_by("total", "DESC")
         .limit(20)
         .build())
    assert "SELECT orders.id, users.name" in q.sql
    assert "INNER JOIN users" in q.sql
    assert "INNER JOIN items" in q.sql
    assert "WHERE" in q.sql
    assert "GROUP BY" in q.sql
    assert "HAVING" in q.sql
    assert "ORDER BY total DESC" in q.sql
    assert "LIMIT 20" in q.sql
