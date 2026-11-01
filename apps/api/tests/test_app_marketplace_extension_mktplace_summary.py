from app.services.app_marketplace_extension_mktplace_summary import MktplaceSummaryService

def test_update():
    svc = MktplaceSummaryService()
    svc.update(total_extensions=500, total_developers=200, avg_rating=4.5)
    s = svc.get()
    assert s.total_extensions == 500
    assert s.avg_rating == 4.5

def test_increment():
    svc = MktplaceSummaryService()
    svc.update(total_installs=1000)
    svc.increment("total_installs", 50)
    assert svc.get().total_installs == 1050

def test_highlights():
    svc = MktplaceSummaryService()
    svc.update(total_extensions=500, total_developers=200,
               total_installs=50000, total_revenue_cents=1000000, avg_rating=4.3)
    h = svc.get_highlights()
    assert h["extensions"] == 500
    assert h["installs"] == "50,000"
    assert h["revenue"] == "$10,000.00"
