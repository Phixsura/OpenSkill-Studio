"""API gateway middleware chain — compose and execute middleware pipelines."""
from __future__ import annotations


class MiddlewareChain:
    def __init__(self):
        self._middlewares: list[dict] = []

    def use(self, name: str, handler: callable, order: int = 0) -> dict:
        self._middlewares.append({"name": name, "handler": handler, "order": order})
        self._middlewares.sort(key=lambda m: m["order"])
        return {"name": name, "position": next(i for i, m in enumerate(self._middlewares) if m["name"] == name) + 1}

    def execute(self, context: dict) -> dict:
        ctx = dict(context)
        applied = []
        for mw in self._middlewares:
            try:
                result = mw["handler"](ctx)
                if isinstance(result, dict):
                    ctx.update(result)
                applied.append({"name": mw["name"], "status": "applied"})
                if ctx.get("_abort"):
                    break
            except Exception as e:
                applied.append({"name": mw["name"], "status": "error", "error": str(e)})
                ctx["_abort"] = True
                ctx["_error"] = str(e)
                break
        return {"context": ctx, "middlewares_applied": applied,
                "completed": not ctx.get("_abort", False)}

    def list(self) -> list[str]:
        return [m["name"] for m in self._middlewares]
