"""Tests for Consumer API Endpoint Map service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_endpoint_map import (
    EndpointMap, MapNode, MapEdge,
)


class TestEndpointMap:
    def test_add_nodes_and_edges(self):
        svc = EndpointMap()
        svc.add_node(MapNode("ep1", "Users API", "endpoint", "core"))
        svc.add_node(MapNode("db1", "PostgreSQL", "database", "infra"))
        svc.add_edge(MapEdge("ep1", "db1", "queries", "reads"))
        m = svc.get_map()
        assert m["node_count"] == 2
        assert m["edge_count"] == 1

    def test_neighbors(self):
        svc = EndpointMap()
        svc.add_node(MapNode("a", "A", "endpoint"))
        svc.add_node(MapNode("b", "B", "service"))
        svc.add_node(MapNode("c", "C", "database"))
        svc.add_edge(MapEdge("a", "b", "calls"))
        svc.add_edge(MapEdge("b", "c", "reads"))
        neighbors = svc.get_neighbors("b")
        assert len(neighbors["incoming"]) == 1
        assert len(neighbors["outgoing"]) == 1

    def test_find_path(self):
        svc = EndpointMap()
        for n in ["a", "b", "c", "d"]:
            svc.add_node(MapNode(n, n.upper(), "endpoint"))
        svc.add_edge(MapEdge("a", "b"))
        svc.add_edge(MapEdge("b", "c"))
        svc.add_edge(MapEdge("c", "d"))
        path = svc.find_path("a", "d")
        assert path == ["a", "b", "c", "d"]

    def test_no_path(self):
        svc = EndpointMap()
        svc.add_node(MapNode("a", "A", "endpoint"))
        svc.add_node(MapNode("b", "B", "endpoint"))
        path = svc.find_path("a", "b")
        assert path == []

    def test_groups(self):
        svc = EndpointMap()
        svc.add_node(MapNode("ep1", "Users", "endpoint", "core"))
        svc.add_node(MapNode("ep2", "Orders", "endpoint", "core"))
        svc.add_node(MapNode("db1", "DB", "database", "infra"))
        m = svc.get_map()
        assert "core" in m["groups"]
        assert "infra" in m["groups"]

    def test_remove_node(self):
        svc = EndpointMap()
        svc.add_node(MapNode("a", "A", "endpoint"))
        svc.add_node(MapNode("b", "B", "endpoint"))
        svc.add_edge(MapEdge("a", "b"))
        svc.remove_node("a")
        assert svc.get_map()["node_count"] == 1
        assert svc.get_map()["edge_count"] == 0

    def test_self_edge_rejected(self):
        svc = EndpointMap()
        svc.add_node(MapNode("a", "A", "endpoint"))
        with pytest.raises(ValueError):
            svc.add_edge(MapEdge("a", "a"))

    def test_missing_node_edge(self):
        svc = EndpointMap()
        svc.add_node(MapNode("a", "A", "endpoint"))
        with pytest.raises(ValueError):
            svc.add_edge(MapEdge("a", "missing"))

    def test_stats(self):
        svc = EndpointMap()
        svc.add_node(MapNode("ep1", "A", "endpoint", "g1"))
        svc.add_node(MapNode("db1", "B", "database", "g2"))
        stats = svc.get_stats()
        assert stats["nodes"] == 2
        assert stats["by_type"]["endpoint"] == 1

    def test_duplicate_node(self):
        svc = EndpointMap()
        svc.add_node(MapNode("a", "A", "endpoint"))
        with pytest.raises(ValueError):
            svc.add_node(MapNode("a", "B", "service"))

    def test_isolation(self):
        a, b = EndpointMap(), EndpointMap()
        a.add_node(MapNode("x", "X", "endpoint"))
        assert b.get_stats()["nodes"] == 0
