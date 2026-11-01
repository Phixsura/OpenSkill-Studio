"""Consumer API Gateway Middleware — configure middleware chains per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class Middleware:
    middleware_id: str
    name: str
    middleware_type: str  # "auth", "rate_limit", "cors", "logging", "compression", "cache", "transform"
    config: dict[str, str] = field(default_factory=dict)
    order: int = 0
    enabled: bool = True

@dataclass
class MiddlewareChain:
    consumer_id: str
    middlewares: list[Middleware] = field(default_factory=list)

@dataclass
class MiddlewareExecutionResult:
    total: int
    executed: int
    skipped: int
    chain: list[str]

VALID_TYPES = {"auth", "rate_limit", "cors", "logging", "compression", "cache", "transform", "validation", "metrics"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiGatewayMiddleware:
    def __init__(self) -> None:
        self._chains: dict[tuple[str, str], MiddlewareChain] = {}

    def add_middleware(self, installation_id: str, consumer_id: str, middleware: Middleware) -> Middleware:
        if not installation_id:
            raise ValueError("installation_id is required")
        if middleware.middleware_type not in VALID_TYPES:
            raise ValueError(f"Invalid middleware_type: {middleware.middleware_type}")
        key = (installation_id, consumer_id)
        if key not in self._chains:
            self._chains[key] = MiddlewareChain(consumer_id=consumer_id)
        chain = self._chains[key]
        # Prevent duplicate IDs
        if any(m.middleware_id == middleware.middleware_id for m in chain.middlewares):
            raise ValueError(f"Middleware {middleware.middleware_id} already exists")
        chain.middlewares.append(middleware)
        chain.middlewares.sort(key=lambda m: m.order)
        return middleware

    def remove_middleware(self, installation_id: str, consumer_id: str, middleware_id: str) -> None:
        key = (installation_id, consumer_id)
        chain = self._chains.get(key)
        if not chain:
            raise ValueError("Chain not found")
        before = len(chain.middlewares)
        chain.middlewares = [m for m in chain.middlewares if m.middleware_id != middleware_id]
        if len(chain.middlewares) == before:
            raise ValueError("Middleware not found")

    def execute_chain(self, installation_id: str, consumer_id: str) -> MiddlewareExecutionResult:
        key = (installation_id, consumer_id)
        chain = self._chains.get(key)
        if not chain:
            return MiddlewareExecutionResult(total=0, executed=0, skipped=0, chain=[])
        executed = []
        skipped = 0
        for m in chain.middlewares:
            if m.enabled:
                executed.append(m.name)
            else:
                skipped += 1
        return MiddlewareExecutionResult(total=len(chain.middlewares), executed=len(executed), skipped=skipped, chain=executed)

    def get_chain(self, installation_id: str, consumer_id: str) -> list[Middleware]:
        chain = self._chains.get((installation_id, consumer_id))
        return chain.middlewares if chain else []
