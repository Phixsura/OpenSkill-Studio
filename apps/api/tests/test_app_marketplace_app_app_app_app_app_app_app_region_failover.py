from app.services.app_marketplace_app_app_app_app_app_app_app_region_failover import (
    create_region_config, check_failover_needed, execute_failover,
)

def test_no_failover():
    regions = [{"name": "us-east", "role": "primary", "healthy": True},
               {"name": "eu-west", "role": "standby", "healthy": True}]
    r = check_failover_needed(regions)
    assert not r["failover_needed"]

def test_failover_needed():
    regions = [{"name": "us-east", "role": "primary", "healthy": False},
               {"name": "eu-west", "role": "standby", "healthy": True}]
    r = check_failover_needed(regions)
    assert r["failover_needed"]
    assert r["candidate"] == "eu-west"

def test_execute():
    regions = [{"name": "us-east", "role": "primary"}, {"name": "eu-west", "role": "standby"}]
    r = execute_failover(regions, "eu-west")
    assert r["new_primary"] == "eu-west"
    assert regions[0]["role"] == "standby"
    assert regions[1]["role"] == "primary"
