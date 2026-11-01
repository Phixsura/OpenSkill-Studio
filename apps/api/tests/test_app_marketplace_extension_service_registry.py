from app.services.app_marketplace_extension_service_registry import ServiceRegistryService
import time


def test_register_and_discover():
    reg = ServiceRegistryService()
    reg.register("api", "host1", 8080)
    reg.register("api", "host2", 8080)
    instances = reg.discover("api")
    assert len(instances) == 2


def test_deregister():
    reg = ServiceRegistryService()
    inst = reg.register("api", "host1", 8080)
    reg.deregister(inst.instance_id)
    assert len(reg.discover("api")) == 0


def test_heartbeat():
    reg = ServiceRegistryService()
    inst = reg.register("api", "host1", 8080)
    assert reg.heartbeat(inst.instance_id, load=0.5) is True
    assert inst.load == 0.5


def test_health_check_expires():
    reg = ServiceRegistryService()
    reg.HEARTBEAT_TTL = 0.01
    inst = reg.register("api", "host1", 8080)
    time.sleep(0.02)
    marked = reg.check_health()
    assert marked == 1
    assert inst.healthy is False


def test_discover_healthy_only():
    reg = ServiceRegistryService()
    i1 = reg.register("api", "host1", 8080)
    i2 = reg.register("api", "host2", 8080)
    i2.healthy = False
    instances = reg.discover("api", healthy_only=True)
    assert len(instances) == 1
    assert instances[0].host == "host1"


def test_tag_filtering():
    reg = ServiceRegistryService()
    reg.register("api", "h1", 8080, tags=["v2", "canary"])
    reg.register("api", "h2", 8080, tags=["v1", "stable"])
    reg.register("api", "h3", 8080, tags=["v2", "stable"])
    instances = reg.discover("api", tags=["v2"])
    assert len(instances) == 2
    instances = reg.discover("api", tags=["v2", "stable"])
    assert len(instances) == 1


def test_resolve_least_load():
    reg = ServiceRegistryService()
    i1 = reg.register("api", "h1", 8080)
    i2 = reg.register("api", "h2", 8080)
    reg.heartbeat(i1.instance_id, load=0.8)
    reg.heartbeat(i2.instance_id, load=0.2)
    chosen = reg.resolve("api", strategy="least_load")
    assert chosen.host == "h2"


def test_resolve_no_instances():
    reg = ServiceRegistryService()
    assert reg.resolve("nonexistent") is None


def test_all_services():
    reg = ServiceRegistryService()
    reg.register("api", "h1", 8080)
    reg.register("api", "h2", 8080)
    reg.register("worker", "h3", 9090)
    services = reg.get_all_services()
    assert services["api"] == 2
    assert services["worker"] == 1


def test_address():
    reg = ServiceRegistryService()
    inst = reg.register("api", "10.0.0.1", 8080)
    assert inst.address == "10.0.0.1:8080"
