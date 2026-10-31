import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_endpoint_dependency_graph import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiEndpointDependencyGraph, DependencyEdge,
)

class TestEndpointDependencyGraph:
    def test_add_and_build(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiEndpointDependencyGraph()
        svc.add_edge("inst-1", DependencyEdge(from_endpoint="/gateway", to_endpoint="/users"))
        svc.add_edge("inst-1", DependencyEdge(from_endpoint="/gateway", to_endpoint="/orders"))
        svc.add_edge("inst-1", DependencyEdge(from_endpoint="/orders", to_endpoint="/inventory"))
        graph = svc.build_graph("inst-1")
        assert graph.total_endpoints == 4 and graph.max_depth == 2

    def test_root_and_leaf(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiEndpointDependencyGraph()
        svc.add_edge("inst-1", DependencyEdge(from_endpoint="/a", to_endpoint="/b"))
        graph = svc.build_graph("inst-1")
        roots = [n for n in graph.nodes if n.is_root]
        leaves = [n for n in graph.nodes if n.is_leaf]
        assert len(roots) == 1 and roots[0].path == "/a"
        assert len(leaves) == 1 and leaves[0].path == "/b"

    def test_record_call(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiEndpointDependencyGraph()
        svc.record_call("inst-1", "/a", "/b", 50)
        svc.record_call("inst-1", "/a", "/b", 100)
        graph = svc.build_graph("inst-1")
        edge = graph.edges[0]
        assert edge.call_count == 2 and 74 < edge.avg_latency_ms < 76

    def test_self_loop_rejected(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiEndpointDependencyGraph()
        with pytest.raises(ValueError, match="Self-loop"):
            svc.add_edge("inst-1", DependencyEdge(from_endpoint="/x", to_endpoint="/x"))

    def test_empty_graph(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiEndpointDependencyGraph()
        graph = svc.build_graph("inst-1")
        assert graph.total_endpoints == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiEndpointDependencyGraph()
        svc.add_edge("inst-1", DependencyEdge(from_endpoint="/a", to_endpoint="/b"))
        assert svc.build_graph("inst-2").total_endpoints == 0
