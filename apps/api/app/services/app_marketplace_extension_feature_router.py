"""Feature Toggle Router — route requests based on feature flags.

Combines feature flags with request routing: different code paths,
different backends, or different UIs based on flag state.

Implements:
- Route mapping: feature flag → handler/target
- Gradual rollout with percentage-based routing
- A/B routing with metrics collection per variant
- Fallback chain when feature disabled
- Override per user/session
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
from collections import defaultdict


@dataclass
class RouteVariant:
    name: str
    target: str  # handler name or URL
    weight: int = 100  # 0-100


@dataclass
class FeatureRoute:
    feature: str
    variants: list[RouteVariant]
    enabled: bool = True
    fallback: str = "default"
    overrides: dict[str, str] = field(default_factory=dict)  # user_id → variant_name


class FeatureRouterService:
    def __init__(self):
        self._routes: dict[str, FeatureRoute] = {}
        self._metrics: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def define_route(self, feature: str, variants: list[tuple[str, str, int]],
                     fallback: str = "default") -> FeatureRoute:
        """variants: [(name, target, weight), ...]"""
        vs = [RouteVariant(name=n, target=t, weight=w) for n, t, w in variants]
        route = FeatureRoute(feature=feature, variants=vs, fallback=fallback)
        self._routes[feature] = route
        return route

    def route(self, feature: str, user_id: str = "",
              session_id: str = "") -> dict:
        """Route a request based on feature flag state."""
        route = self._routes.get(feature)
        if not route or not route.enabled:
            return {"target": route.fallback if route else "default",
                    "variant": "fallback", "feature": feature}

        # Check user override
        if user_id and user_id in route.overrides:
            variant_name = route.overrides[user_id]
            for v in route.variants:
                if v.name == variant_name:
                    self._metrics[feature][variant_name] += 1
                    return {"target": v.target, "variant": v.name,
                            "feature": feature, "override": True}

        # Weighted selection via hash
        routing_key = user_id or session_id or "anonymous"
        h = int(hashlib.md5(f"{feature}:{routing_key}".encode()).hexdigest()[:8], 16)
        bucket = h % 100

        cumulative = 0
        for variant in route.variants:
            cumulative += variant.weight
            if bucket < cumulative:
                self._metrics[feature][variant.name] += 1
                return {"target": variant.target, "variant": variant.name,
                        "feature": feature}

        # Fallback
        return {"target": route.fallback, "variant": "fallback",
                "feature": feature}

    def set_override(self, feature: str, user_id: str,
                     variant_name: str) -> bool:
        route = self._routes.get(feature)
        if not route:
            return False
        route.overrides[user_id] = variant_name
        return True

    def clear_override(self, feature: str, user_id: str) -> bool:
        route = self._routes.get(feature)
        if route and user_id in route.overrides:
            del route.overrides[user_id]
            return True
        return False

    def toggle(self, feature: str, enabled: bool) -> bool:
        route = self._routes.get(feature)
        if route:
            route.enabled = enabled
            return True
        return False

    def get_metrics(self, feature: str) -> dict:
        m = self._metrics.get(feature, {})
        total = sum(m.values())
        return {
            "feature": feature,
            "total_routed": total,
            "by_variant": dict(m),
            "distribution": {k: round(v / max(1, total) * 100, 1)
                             for k, v in m.items()},
        }
