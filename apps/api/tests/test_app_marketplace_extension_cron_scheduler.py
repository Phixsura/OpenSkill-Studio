from app.services.app_marketplace_extension_cron_scheduler import ExtCronSchedulerService

def test_create_and_trigger():
    svc = ExtCronSchedulerService()
    job = svc.create("ext-1", "Daily Sync", "0 0 * * *", "/sync")
    assert svc.trigger(job.job_id) is True
    assert job.run_count == 1

def test_invalid_cron():
    svc = ExtCronSchedulerService()
    try:
        svc.create("ext-1", "Bad", "not valid", "/x")
        assert False
    except ValueError:
        pass

def test_toggle():
    svc = ExtCronSchedulerService()
    job = svc.create("ext-1", "Job", "*/5 * * * *", "/run")
    svc.toggle(job.job_id, False)
    assert svc.trigger(job.job_id) is False

def test_delete():
    svc = ExtCronSchedulerService()
    job = svc.create("ext-1", "Job", "0 * * * *", "/hourly")
    assert svc.delete(job.job_id) is True
    assert len(svc.get_by_extension("ext-1")) == 0
