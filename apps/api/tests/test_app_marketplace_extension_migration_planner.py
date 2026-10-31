from app.services.app_marketplace_extension_migration_planner import (
    MigrationPlanner, RolloutStrategy,
)


def test_create_plan():
    mp = MigrationPlanner()
    plan = mp.create_plan("m1", "ext-1", "1.0", "2.0",
                           ["org-a", "org-b", "org-c"], RolloutStrategy.ROLLING)
    assert len(plan.orgs) == 3
    assert all(o.status == "pending" for o in plan.orgs)


def test_rolling_batch():
    mp = MigrationPlanner()
    mp.create_plan("m2", "ext-2", "1.0", "2.0",
                    ["o1", "o2", "o3"], RolloutStrategy.ROLLING)
    batch = mp.get_next_batch("m2")
    assert len(batch) == 1  # rolling: one at a time


def test_all_at_once_batch():
    mp = MigrationPlanner()
    mp.create_plan("m3", "ext-3", "1.0", "2.0",
                    ["o1", "o2", "o3"], RolloutStrategy.ALL_AT_ONCE)
    batch = mp.get_next_batch("m3")
    assert len(batch) == 3


def test_canary_batch():
    mp = MigrationPlanner()
    mp.create_plan("m4", "ext-4", "1.0", "2.0",
                    [f"o{i}" for i in range(20)], RolloutStrategy.CANARY, canary_percent=10)
    batch = mp.get_next_batch("m4")
    assert len(batch) == 2  # 10% of 20


def test_migrate_and_progress():
    mp = MigrationPlanner()
    mp.create_plan("m5", "ext-5", "1.0", "2.0", ["o1", "o2", "o3"])
    mp.migrate_org("m5", "o1", True)
    mp.migrate_org("m5", "o2", False, "Connection error")
    progress = mp.get_progress("m5")
    assert progress["by_status"]["completed"] == 1
    assert progress["by_status"]["failed"] == 1
    assert progress["has_failures"] is True


def test_rollback():
    mp = MigrationPlanner()
    mp.create_plan("m6", "ext-6", "1.0", "2.0", ["o1"])
    mp.migrate_org("m6", "o1", True)
    mp.rollback_org("m6", "o1")
    progress = mp.get_progress("m6")
    assert progress["by_status"]["rolled_back"] == 1
