"""Consumer API Dependency Injection — manage service bindings per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ServiceBinding:
    binding_id: str
    interface_name: str
    implementation: str
    scope: str = "singleton"  # "singleton", "transient", "scoped"
    config: dict[str, str] = field(default_factory=dict)
    active: bool = True

@dataclass
class ResolutionResult:
    interface_name: str
    implementation: str
    scope: str
    resolved: bool

VALID_SCOPES = {"singleton", "transient", "scoped"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiDependencyInjection:
    def __init__(self) -> None:
        self._bindings: dict[tuple[str, str, str], ServiceBinding] = {}  # (inst, consumer, interface)

    def bind(self, installation_id: str, consumer_id: str, binding: ServiceBinding) -> ServiceBinding:
        if not installation_id:
            raise ValueError("installation_id is required")
        if binding.scope not in VALID_SCOPES:
            raise ValueError(f"Invalid scope: {binding.scope}")
        if not binding.interface_name:
            raise ValueError("interface_name is required")
        key = (installation_id, consumer_id, binding.interface_name)
        self._bindings[key] = binding
        log.info("binding_registered", installation_id=installation_id, interface=binding.interface_name, impl=binding.implementation)
        return binding

    def resolve(self, installation_id: str, consumer_id: str, interface_name: str) -> ResolutionResult:
        key = (installation_id, consumer_id, interface_name)
        binding = self._bindings.get(key)
        if not binding or not binding.active:
            return ResolutionResult(interface_name=interface_name, implementation="", scope="", resolved=False)
        return ResolutionResult(interface_name=interface_name, implementation=binding.implementation, scope=binding.scope, resolved=True)

    def unbind(self, installation_id: str, consumer_id: str, interface_name: str) -> None:
        key = (installation_id, consumer_id, interface_name)
        if key not in self._bindings:
            raise ValueError("Binding not found")
        del self._bindings[key]

    def list_bindings(self, installation_id: str, consumer_id: str) -> list[ServiceBinding]:
        return sorted([b for (inst, cid, _), b in self._bindings.items() if inst == installation_id and cid == consumer_id], key=lambda b: b.interface_name)

    def resolve_all(self, installation_id: str, consumer_id: str) -> dict[str, str]:
        bindings = self.list_bindings(installation_id, consumer_id)
        return {b.interface_name: b.implementation for b in bindings if b.active}
