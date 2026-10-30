"""API Consumer API Key IP Binding — bind API keys to specific IP addresses."""
from __future__ import annotations
from dataclasses import dataclass, field
import ipaddress
import structlog

log = structlog.get_logger()

@dataclass
class IpBinding:
    key_id: str
    consumer_id: str
    allowed_ips: list[str] = field(default_factory=list)  # IPs or CIDRs
    enforce: bool = True
    violations: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyIpBinding:
    def __init__(self) -> None:
        self._bindings: dict[tuple[str, str], IpBinding] = {}

    def bind(self, installation_id: str, binding: IpBinding) -> IpBinding:
        if not installation_id: raise ValueError("installation_id is required")
        if not binding.allowed_ips: raise ValueError("At least one IP required")
        for ip in binding.allowed_ips:
            try: ipaddress.ip_network(ip, strict=False)
            except ValueError as e: raise ValueError(f"Invalid IP/CIDR: {ip}") from e
        self._bindings[(installation_id, binding.key_id)] = binding
        return binding

    def check(self, installation_id: str, key_id: str, client_ip: str) -> bool:
        binding = self._bindings.get((installation_id, key_id))
        if binding is None: return True  # no binding = allow
        if not binding.enforce: return True
        try:
            addr = ipaddress.ip_address(client_ip)
        except ValueError:
            binding.violations += 1
            return False
        for allowed in binding.allowed_ips:
            net = ipaddress.ip_network(allowed, strict=False)
            if addr in net: return True
        binding.violations += 1
        return False

    def get_binding(self, installation_id: str, key_id: str) -> IpBinding | None:
        return self._bindings.get((installation_id, key_id))

    def list_bindings(self, installation_id: str) -> list[IpBinding]:
        return [b for (inst, _), b in self._bindings.items() if inst == installation_id]
