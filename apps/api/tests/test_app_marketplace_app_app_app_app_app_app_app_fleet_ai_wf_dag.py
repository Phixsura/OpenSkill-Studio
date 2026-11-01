from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_wf_dag import fleet_ai_workflow_dag
def test_dag():
    r = fleet_ai_workflow_dag([{"active": True, "dags_24h": 10000, "nodes": 500000, "avg_parallelism": 8}])
    assert r["dags_24h"] == 10000
    assert r["efficient"]
