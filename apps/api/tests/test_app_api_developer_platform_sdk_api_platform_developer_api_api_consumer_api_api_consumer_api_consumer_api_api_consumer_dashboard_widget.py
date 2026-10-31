import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_dashboard_widget import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerDashboardWidget, DashboardWidget,
)

class TestConsumerApiDashboardWidget:
    def test_add_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerDashboardWidget()
        svc.add_widget("inst-1", "c1", DashboardWidget(widget_id="w1", widget_type="metric", title="API Calls", position=0))
        dash = svc.get_dashboard("inst-1", "c1")
        assert dash is not None and len(dash.widgets) == 1

    def test_reorder(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerDashboardWidget()
        svc.add_widget("inst-1", "c1", DashboardWidget(widget_id="w1", widget_type="metric", title="A", position=0))
        svc.add_widget("inst-1", "c1", DashboardWidget(widget_id="w2", widget_type="chart", title="B", position=1))
        widgets = svc.reorder("inst-1", "c1", ["w2", "w1"])
        assert widgets[0].widget_id == "w2"

    def test_hidden_filtered(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerDashboardWidget()
        svc.add_widget("inst-1", "c1", DashboardWidget(widget_id="w1", widget_type="metric", title="A", visible=True))
        svc.add_widget("inst-1", "c1", DashboardWidget(widget_id="w2", widget_type="chart", title="B", visible=False))
        visible = svc.get_visible_widgets("inst-1", "c1")
        assert len(visible) == 1

    def test_remove(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerDashboardWidget()
        svc.add_widget("inst-1", "c1", DashboardWidget(widget_id="w1", widget_type="metric", title="A"))
        svc.remove_widget("inst-1", "c1", "w1")
        assert len(svc.get_visible_widgets("inst-1", "c1")) == 0

    def test_duplicate_widget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerDashboardWidget()
        svc.add_widget("inst-1", "c1", DashboardWidget(widget_id="w1", widget_type="metric", title="A"))
        with pytest.raises(ValueError, match="already exists"):
            svc.add_widget("inst-1", "c1", DashboardWidget(widget_id="w1", widget_type="chart", title="B"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerDashboardWidget()
        svc.add_widget("inst-1", "c1", DashboardWidget(widget_id="w1", widget_type="metric", title="A"))
        assert svc.get_dashboard("inst-2", "c1") is None
