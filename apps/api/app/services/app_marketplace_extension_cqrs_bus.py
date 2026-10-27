"""CQRS Command Bus — separate command and query pipelines with middleware.

Implements:
- Type-safe command/query dispatch via handler registry
- Pre/post middleware pipeline (validation, logging, auth)
- Command deduplication via idempotency key
- Async-style result tracking
- Dead letter queue for failed commands
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class Command:
    command_type: str
    payload: dict
    idempotency_key: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class CommandResult:
    success: bool
    data: dict = field(default_factory=dict)
    error: str = ""
    duration_ms: float = 0.0


@dataclass
class Query:
    query_type: str
    params: dict = field(default_factory=dict)


class CqrsCommandBusService:
    def __init__(self):
        self._command_handlers: dict[str, callable] = {}
        self._query_handlers: dict[str, callable] = {}
        self._pre_middleware: list[callable] = []
        self._post_middleware: list[callable] = []
        self._processed_keys: set[str] = set()
        self._dead_letter: list[tuple[Command, str]] = []
        self._history: list[tuple[Command, CommandResult]] = []

    def register_command(self, command_type: str, handler: callable) -> None:
        if command_type in self._command_handlers:
            raise ValueError(f"Handler already registered for {command_type}")
        self._command_handlers[command_type] = handler

    def register_query(self, query_type: str, handler: callable) -> None:
        self._query_handlers[query_type] = handler

    def add_pre_middleware(self, middleware: callable) -> None:
        self._pre_middleware.append(middleware)

    def add_post_middleware(self, middleware: callable) -> None:
        self._post_middleware.append(middleware)

    def dispatch(self, command: Command) -> CommandResult:
        start = time.time()

        # Idempotency check
        if command.idempotency_key:
            if command.idempotency_key in self._processed_keys:
                return CommandResult(success=True, data={"deduplicated": True})
            self._processed_keys.add(command.idempotency_key)

        # Find handler
        handler = self._command_handlers.get(command.command_type)
        if not handler:
            result = CommandResult(success=False, error=f"No handler for {command.command_type}")
            self._dead_letter.append((command, result.error))
            return result

        # Pre-middleware
        for mw in self._pre_middleware:
            rejection = mw(command)
            if rejection:
                return CommandResult(success=False, error=f"Rejected by middleware: {rejection}")

        # Execute
        try:
            data = handler(command.payload)
            duration = round((time.time() - start) * 1000, 2)
            result = CommandResult(success=True, data=data or {}, duration_ms=duration)
        except Exception as e:
            duration = round((time.time() - start) * 1000, 2)
            result = CommandResult(success=False, error=str(e), duration_ms=duration)
            self._dead_letter.append((command, str(e)))

        # Post-middleware
        for mw in self._post_middleware:
            mw(command, result)

        self._history.append((command, result))
        return result

    def query(self, q: Query) -> dict:
        handler = self._query_handlers.get(q.query_type)
        if not handler:
            raise ValueError(f"No query handler for {q.query_type}")
        return handler(q.params)

    def get_dead_letters(self) -> list[tuple[Command, str]]:
        return list(self._dead_letter)

    def get_history(self, limit: int = 50) -> list[dict]:
        return [{"command": c.command_type, "success": r.success,
                 "duration_ms": r.duration_ms}
                for c, r in self._history[-limit:]]
