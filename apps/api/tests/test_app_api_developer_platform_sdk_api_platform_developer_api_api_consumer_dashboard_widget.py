import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_dashboard_widget import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDashboardWidget, Dashboard, DashboardWidget,
)

class TestConsumerDashboardWidget:
    def test_create_and_add_widget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDashboardWidget()
        svc.create_dashboard("inst-1", Dashboard(dashboard_id="d1", consumer_id="c1"))
        d = svc.add_widget("inst-1", "d1", DashboardWidget(widget_id="w1", widget_type="chart", title="Requests", data_source="requests"))
        assert len(d.widgets) == 1

    def test_invalid_widget_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDashboardWidget()
        svc.create_dashboard("inst-1", Dashboard(dashboard_id="d1", consumer_id="c1"))
        with pytest.raises(ValueError, match="Invalid type"):
            svc.add_widget("inst-1", "d1", DashboardWidget(widget_id="w1", widget_type="bad", title="X", data_source="requests"))

    def test_remove_widget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDashboardWidget()
        svc.create_dashboard("inst-1", Dashboard(dashboard_id="d1", consumer_id="c1"))
        svc.add_widget("inst-1", "d1", DashboardWidget(widget_id="w1", widget_type="counter", title="Errors", data_source="errors"))
        d = svc.remove_widget("inst-1", "d1", "w1")
        assert len(d.widgets) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDashboardWidget()
        svc.create_dashboard("inst-1", Dashboard(dashboard_id="d1", consumer_id="c1"))
        assert len(svc.list_dashboards("inst-2")) == 0
