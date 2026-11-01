from app.services.app_marketplace_graph_resolver import (
    ExtensionGraphResolver, RelationType,
)


def test_add_and_query():
    gr = ExtensionGraphResolver()
    gr.add_relationship("app", "core", RelationType.DEPENDS_ON)
    outgoing = gr.get_outgoing("app")
    assert len(outgoing) == 1
    assert outgoing[0].target == "core"
    incoming = gr.get_incoming("core")
    assert len(incoming) == 1


def test_transitive_dependencies():
    gr = ExtensionGraphResolver()
    gr.add_relationship("app", "middleware", RelationType.DEPENDS_ON)
    gr.add_relationship("middleware", "core", RelationType.DEPENDS_ON)
    gr.add_relationship("core", "utils", RelationType.DEPENDS_ON)
    deps = gr.get_dependencies("app")
    assert deps == ["core", "middleware", "utils"]


def test_transitive_dependents():
    gr = ExtensionGraphResolver()
    gr.add_relationship("app-a", "lib", RelationType.DEPENDS_ON)
    gr.add_relationship("app-b", "lib", RelationType.DEPENDS_ON)
    gr.add_relationship("app-c", "app-a", RelationType.DEPENDS_ON)
    dependents = gr.get_dependents("lib")
    assert "app-a" in dependents
    assert "app-b" in dependents
    assert "app-c" in dependents


def test_impact_analysis():
    gr = ExtensionGraphResolver()
    for i in range(6):
        gr.add_relationship(f"app-{i}", "shared-lib", RelationType.DEPENDS_ON)
    gr.add_relationship("new-lib", "shared-lib", RelationType.REPLACES)
    impact = gr.impact_analysis("shared-lib")
    assert impact["direct_dependents"] == 6
    assert impact["high_impact"] is True
    assert "new-lib" in impact["can_be_replaced_by"]


def test_integrations():
    gr = ExtensionGraphResolver()
    gr.add_relationship("slack-ext", "analytics-ext", RelationType.INTEGRATES_WITH)
    incoming = gr.get_incoming("analytics-ext", RelationType.INTEGRATES_WITH)
    assert len(incoming) == 1


def test_all_nodes():
    gr = ExtensionGraphResolver()
    gr.add_relationship("a", "b", RelationType.DEPENDS_ON)
    gr.add_relationship("b", "c", RelationType.EXTENDS)
    assert gr.get_all_nodes() == ["a", "b", "c"]
