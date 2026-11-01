import pytest
from app.services.app_api_endpoint_deprecation_notice import AppAPIEndpointDeprecationNotice

class TestNotice:
    def test_create(self):
        n = AppAPIEndpointDeprecationNotice()
        notice = n.create("inst-1", "n1", "GET", "/api/v1/users", "Use v2", "2025-01-01", "/api/v2/users")
        assert notice.sunset_date == "2025-01-01"

    def test_acknowledge(self):
        n = AppAPIEndpointDeprecationNotice()
        n.create("inst-1", "n1", "GET", "/api/v1", "Use v2", "2025-01")
        n.acknowledge("inst-1", "n1", "consumer-a")
        assert n.unacknowledged_count("inst-1", "n1", 5) == 4

    def test_duplicate(self):
        n = AppAPIEndpointDeprecationNotice()
        n.create("inst-1", "n1", "GET", "/a", "M", "2025")
        with pytest.raises(ValueError):
            n.create("inst-1", "n1", "POST", "/b", "M", "2025")

    def test_isolation(self):
        n = AppAPIEndpointDeprecationNotice()
        n.create("inst-1", "n1", "GET", "/a", "M", "2025")
        assert n.list_notices("inst-2") == []
