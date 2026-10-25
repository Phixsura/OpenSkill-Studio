from app.services.app_marketplace_service_discovery import (
    ServiceDiscovery, ServiceInstance,
)


def test_register_and_discover():
    sd = ServiceDiscovery()
    sd.register(ServiceInstance("i1", "ext-1", "auth", "http://ext1:8080/auth", "1.0.0"))
    sd.register(ServiceInstance("i2", "ext-1", "auth", "http://ext1:8081/auth", "1.0.0"))
    instances = sd.discover("auth")
    assert len(instances) == 2


def test_discover_by_extension():
    sd = ServiceDiscovery()
    sd.register(ServiceInstance("i3", "ext-a", "api", "http://a:80", "1.0"))
    sd.register(ServiceInstance("i4", "ext-b", "api", "http://b:80", "1.0"))
    instances = sd.discover("api", extension_id="ext-a")
    assert len(instances) == 1
    assert instances[0].extension_id == "ext-a"


def test_deregister():
    sd = ServiceDiscovery()
    sd.register(ServiceInstance("i5", "ext-1", "cache", "http://c:80", "1.0"))
    assert sd.deregister("i5") is True
    assert sd.discover("cache") == []


def test_heartbeat():
    sd = ServiceDiscovery()
    sd.register(ServiceInstance("i6", "ext-1", "db", "http://db:80", "1.0"))
    assert sd.heartbeat("i6") is True
    assert sd.heartbeat("nonexistent") is False


def test_unhealthy_after_timeout():
    sd = ServiceDiscovery(heartbeat_timeout=0.0)  # immediate timeout
    inst = ServiceInstance("i7", "ext-1", "worker", "http://w:80", "1.0")
    inst.last_heartbeat = 0  # long ago
    sd.register(inst)
    healthy = sd.discover("worker", healthy_only=True)
    assert len(healthy) == 0
    all_inst = sd.discover("worker", healthy_only=False)
    assert len(all_inst) == 1
    assert all_inst[0].healthy is False


def test_list_services():
    sd = ServiceDiscovery()
    sd.register(ServiceInstance("s1", "ext-1", "api", "http://a:80", "1.0"))
    sd.register(ServiceInstance("s2", "ext-1", "api", "http://b:80", "1.0"))
    sd.register(ServiceInstance("s3", "ext-2", "worker", "http://c:80", "1.0"))
    services = sd.list_services()
    assert len(services) == 2
    api_svc = next(s for s in services if s["name"] == "api")
    assert api_svc["total"] == 2
