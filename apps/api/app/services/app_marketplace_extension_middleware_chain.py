"""Middleware Chain — composable request/response pipeline with next() semantics.

Like Express.js/Koa middleware: each middleware can modify the request,
call next() to pass to the next middleware, then modify the response.

Implements:
- Ordered middleware chain with priority
- Before/after hooks (onion model)
- Short-circuit (skip remaining middleware)
- Error middleware (catch errors from inner layers)
- Conditional middleware (only runs if predicate matches)
- Timing per middleware
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class Context:
    request: dict = field(default_factory=dict)
    response: dict = field(default_factory=dict)
    state: dict = field(default_factory=dict)  # shared state across middleware
    error: str = ""
    aborted: bool = False
    timings: dict[str, float] = field(default_factory=dict)


@dataclass
class Middleware:
    name: str
    handler: callable  # (ctx, next_fn) -> None
    priority: int = 0  # higher = runs first (outer layer)
    condition: callable | None = None  # (ctx) -> bool
    error_handler: bool = False  # only runs on error


class MiddlewareChainService:
    def __init__(self):
        self._middleware: list[Middleware] = []

    def use(self, name: str, handler: callable, priority: int = 0,
            condition: callable | None = None) -> None:
        self._middleware.append(Middleware(name=name, handler=handler,
                                          priority=priority, condition=condition))
        self._middleware.sort(key=lambda m: m.priority, reverse=True)

    def use_error(self, name: str, handler: callable) -> None:
        """Register error-handling middleware."""
        self._middleware.append(Middleware(name=name, handler=handler,
                                          error_handler=True))

    def execute(self, ctx: Context | None = None) -> Context:
        """Execute the middleware chain."""
        ctx = ctx or Context()
        chain = [m for m in self._middleware if not m.error_handler]
        error_handlers = [m for m in self._middleware if m.error_handler]

        try:
            self._run_chain(chain, 0, ctx)
        except Exception as e:
            ctx.error = str(e)
            # Run error handlers
            for eh in error_handlers:
                try:
                    eh.handler(ctx)
                except Exception:
                    pass

        return ctx

    def _run_chain(self, chain: list[Middleware], index: int, ctx: Context) -> None:
        if ctx.aborted or index >= len(chain):
            return

        middleware = chain[index]

        # Check condition
        if middleware.condition and not middleware.condition(ctx):
            self._run_chain(chain, index + 1, ctx)
            return

        start = time.time()
        called_next = [False]

        def next_fn():
            called_next[0] = True
            self._run_chain(chain, index + 1, ctx)

        middleware.handler(ctx, next_fn)
        ctx.timings[middleware.name] = round((time.time() - start) * 1000, 2)

        # If handler didn't call next, chain stops (short-circuit)

    def get_chain(self) -> list[str]:
        return [m.name for m in self._middleware if not m.error_handler]
