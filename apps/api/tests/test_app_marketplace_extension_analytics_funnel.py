from app.services.app_marketplace_extension_analytics_funnel import (
    AnalyticsFunnelService, FunnelStage,
)


def test_track_and_funnel():
    svc = AnalyticsFunnelService()
    svc.track("ext-1", "u1", FunnelStage.DISCOVERY)
    svc.track("ext-1", "u1", FunnelStage.VIEW)
    svc.track("ext-1", "u1", FunnelStage.INSTALL)
    svc.track("ext-1", "u2", FunnelStage.DISCOVERY)
    svc.track("ext-1", "u2", FunnelStage.VIEW)
    report = svc.get_funnel("ext-1")
    assert report.stages["discovery"] == 2
    assert report.stages["view"] == 2
    assert report.stages["install"] == 1
    assert report.total_users == 2


def test_conversion_rates():
    svc = AnalyticsFunnelService()
    for uid in ["u1", "u2", "u3", "u4"]:
        svc.track("ext-1", uid, FunnelStage.DISCOVERY)
    for uid in ["u1", "u2"]:
        svc.track("ext-1", uid, FunnelStage.VIEW)
    svc.track("ext-1", "u1", FunnelStage.INSTALL)
    report = svc.get_funnel("ext-1")
    assert report.conversion_rates["discovery"] == 100.0
    assert report.conversion_rates["view"] == 50.0
    assert report.conversion_rates["install"] == 25.0


def test_drop_off():
    svc = AnalyticsFunnelService()
    for uid in ["u1", "u2", "u3", "u4"]:
        svc.track("ext-1", uid, FunnelStage.DISCOVERY)
    for uid in ["u1", "u2"]:
        svc.track("ext-1", uid, FunnelStage.VIEW)
    report = svc.get_funnel("ext-1")
    assert report.drop_off["view"] == 50.0


def test_source_breakdown():
    svc = AnalyticsFunnelService()
    svc.track("ext-1", "u1", FunnelStage.DISCOVERY, source="search")
    svc.track("ext-1", "u2", FunnelStage.DISCOVERY, source="browse")
    svc.track("ext-1", "u1", FunnelStage.VIEW, source="search")
    breakdown = svc.get_source_breakdown("ext-1")
    assert breakdown["search"]["discovery"] == 1
    assert breakdown["search"]["view"] == 1
    assert breakdown["browse"]["discovery"] == 1


def test_compare_funnels():
    svc = AnalyticsFunnelService()
    svc.track("ext-1", "u1", FunnelStage.DISCOVERY)
    svc.track("ext-1", "u1", FunnelStage.INSTALL)
    svc.track("ext-2", "u2", FunnelStage.DISCOVERY)
    result = svc.compare_funnels(["ext-1", "ext-2"])
    assert result["ext-1"]["install_rate"] == 100.0
    assert result["ext-2"]["install_rate"] == 0.0


def test_stage_progression():
    svc = AnalyticsFunnelService()
    # Out-of-order tracking should keep highest stage
    svc.track("ext-1", "u1", FunnelStage.INSTALL)
    svc.track("ext-1", "u1", FunnelStage.DISCOVERY)  # lower, ignored
    report = svc.get_funnel("ext-1")
    assert report.stages["install"] == 1
