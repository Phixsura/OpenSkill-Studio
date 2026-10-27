from app.services.app_marketplace_extension_query_planner import QueryPlannerService


def test_full_scan():
    qp = QueryPlannerService()
    qp.register_table("users", row_count=1000, avg_row_size=200)
    plan = qp.plan_scan("users")
    assert plan.strategy == "seq_scan"
    assert plan.estimated_rows == 1000


def test_index_preferred_for_selective():
    qp = QueryPlannerService()
    qp.register_table("users", row_count=100000, avg_row_size=200,
                       indexes=["email"],
                       index_cardinality={"email": 100000})
    plan = qp.plan_scan("users", filter_col="email", selectivity=0.001)
    # Index should be cheaper for highly selective queries
    assert plan.strategy in ("index_scan", "index_only_scan")


def test_seq_scan_when_no_index():
    qp = QueryPlannerService()
    qp.register_table("logs", row_count=10000, avg_row_size=100)
    plan = qp.plan_scan("logs", filter_col="status", selectivity=0.9)
    # No index on status → must use seq scan
    assert plan.strategy == "seq_scan"
    assert plan.estimated_rows == 9000


def test_hash_join_preferred():
    qp = QueryPlannerService()
    qp.register_table("orders", row_count=10000)
    qp.register_table("customers", row_count=1000)
    plan = qp.plan_join("orders", "customers", "customer_id")
    assert plan.strategy == "hash_join"


def test_merge_join_with_indexes():
    qp = QueryPlannerService()
    qp.register_table("a", row_count=10000, indexes=["id"])
    qp.register_table("b", row_count=10000, indexes=["id"])
    plan = qp.plan_join("a", "b", "id")
    assert plan.strategy == "merge_join"


def test_nested_loop_for_small_tables():
    qp = QueryPlannerService()
    qp.register_table("small_a", row_count=10)
    qp.register_table("small_b", row_count=10)
    plan = qp.plan_join("small_a", "small_b", "id")
    # For very small tables, all strategies are cheap
    assert plan.estimated_cost < 10


def test_explain():
    qp = QueryPlannerService()
    qp.register_table("users", row_count=5000)
    plan = qp.plan_scan("users")
    output = qp.explain(plan)
    assert "seq_scan" in output
    assert "cost=" in output


def test_unknown_table():
    qp = QueryPlannerService()
    plan = qp.plan_scan("nonexistent")
    assert plan.strategy == "unknown"
