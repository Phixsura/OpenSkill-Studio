from app.services.app_marketplace_extension_isolation_manager import (
    IsolationManagerService, IsolationLevel, CommunicationPolicy,
)


def test_register():
    svc = IsolationManagerService()
    b = svc.register("sb-1", "tenant-1")
    assert b.isolation_level == IsolationLevel.FULL
    assert b.namespace.startswith("ns_tenant-1_")


def test_deny_all_communication():
    svc = IsolationManagerService()
    svc.register("sb-1", "t1", comm_policy=CommunicationPolicy.DENY_ALL)
    svc.register("sb-2", "t1")
    result = svc.can_communicate("sb-1", "sb-2")
    assert result["allowed"] is False


def test_same_tenant_communication():
    svc = IsolationManagerService()
    svc.register("sb-1", "t1", comm_policy=CommunicationPolicy.ALLOW_SAME_TENANT)
    svc.register("sb-2", "t1")
    svc.register("sb-3", "t2")
    assert svc.can_communicate("sb-1", "sb-2")["allowed"] is True
    assert svc.can_communicate("sb-1", "sb-3")["allowed"] is False


def test_explicit_peer_communication():
    svc = IsolationManagerService()
    svc.register("sb-1", "t1", comm_policy=CommunicationPolicy.ALLOW_EXPLICIT)
    svc.register("sb-2", "t1")
    svc.register("sb-3", "t1")
    svc.allow_peer("sb-1", "sb-2")
    assert svc.can_communicate("sb-1", "sb-2")["allowed"] is True
    assert svc.can_communicate("sb-1", "sb-3")["allowed"] is False


def test_full_isolation_no_shared_volumes():
    svc = IsolationManagerService()
    svc.register("sb-1", "t1", isolation_level=IsolationLevel.FULL)
    assert svc.share_volume("sb-1", "/data") is False


def test_namespace_shared_volumes():
    svc = IsolationManagerService()
    svc.register("sb-1", "t1", isolation_level=IsolationLevel.NAMESPACE)
    assert svc.share_volume("sb-1", "/shared/data") is True
    assert svc.can_access_volume("sb-1", "/shared/data") is True
    assert svc.can_access_volume("sb-1", "/other") is False


def test_tenant_sandboxes():
    svc = IsolationManagerService()
    svc.register("sb-1", "t1")
    svc.register("sb-2", "t1")
    svc.register("sb-3", "t2")
    assert set(svc.get_tenant_sandboxes("t1")) == {"sb-1", "sb-2"}


def test_boundary_info():
    svc = IsolationManagerService()
    svc.register("sb-1", "t1", isolation_level=IsolationLevel.NAMESPACE,
                 comm_policy=CommunicationPolicy.ALLOW_SAME_TENANT)
    info = svc.get_boundary("sb-1")
    assert info["isolation_level"] == "namespace"
    assert info["comm_policy"] == "allow_same_tenant"
