import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_service_mesh_topology import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiServiceMeshTopology, ServiceNode, ServiceEdge,
)

class TestServiceMeshTopology:
    def test_add_nodes_and_edge(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiServiceMeshTopology()
        svc.add_node("inst-1", ServiceNode(service_id="api", name="API Gateway"))
        svc.add_node("inst-1", ServiceNode(service_id="db", name="Database"))
        svc.add_edge("inst-1", ServiceEdge(source_id="api", target_id="db", avg_latency_ms=5))
        deps = svc.get_dependencies("inst-1", "api")
        assert len(deps) == 1 and deps[0].target_id == "db"

    def test_self_loop_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiServiceMeshTopology()
        svc.add_node("inst-1", ServiceNode(service_id="api", name="API"))
        with pytest.raises(ValueError, match="Self-loop"):
            svc.add_edge("inst-1", ServiceEdge(source_id="api", target_id="api"))

    def test_unhealthy_nodes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiServiceMeshTopology()
        svc.add_node("inst-1", ServiceNode(service_id="api", name="API", healthy=True))
        svc.add_node("inst-1", ServiceNode(service_id="db", name="DB", healthy=False))
        assert len(svc.unhealthy_nodes("inst-1")) == 1

    def test_high_latency(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiServiceMeshTopology()
        svc.add_node("inst-1", ServiceNode(service_id="a", name="A"))
        svc.add_node("inst-1", ServiceNode(service_id="b", name="B"))
        svc.add_edge("inst-1", ServiceEdge(source_id="a", target_id="b", avg_latency_ms=500))
        assert len(svc.high_latency_edges("inst-1", 200)) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiServiceMeshTopology()
        svc.add_node("inst-1", ServiceNode(service_id="api", name="API"))
        assert len(svc.list_nodes("inst-2")) == 0
