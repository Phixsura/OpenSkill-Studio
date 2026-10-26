from app.services.app_marketplace_extension_data_export_mgr import DataExportMgrService

def test_create_and_process_json():
    svc = DataExportMgrService()
    job = svc.create_export("u1", "extensions", "json")
    data = [{"id": "ext-1", "name": "Test"}]
    assert svc.process(job.job_id, data) is True
    assert job.status == "completed"
    assert '"name": "Test"' in job.result

def test_csv_export():
    svc = DataExportMgrService()
    job = svc.create_export("u1", "analytics", "csv")
    data = [{"metric": "dau", "value": "100"}, {"metric": "mau", "value": "5000"}]
    svc.process(job.job_id, data)
    assert "metric,value" in job.result
    assert "dau,100" in job.result

def test_invalid_format():
    svc = DataExportMgrService()
    try:
        svc.create_export("u1", "extensions", "xml")
        assert False
    except ValueError:
        pass

def test_user_exports():
    svc = DataExportMgrService()
    svc.create_export("u1", "extensions")
    svc.create_export("u1", "reviews")
    svc.create_export("u2", "extensions")
    assert len(svc.get_user_exports("u1")) == 2
