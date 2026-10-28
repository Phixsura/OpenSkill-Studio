"""App Config Override — layered configuration with environment overrides.

Manages layered configuration for installed apps:
- Base config with environment-specific overrides
- Override priority: env > installation > base
- Resolved config computation
- Per-installation scoped configs
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ConfigLayer:
    """A configuration layer."""

    layer_id: str
    priority: int  # higher = wins
    values: dict = field(default_factory=dict)


class AppConfigOverride:
    """Layered configuration with environment overrides."""

    def __init__(self) -> None:
        # (installation_id, layer_id) → ConfigLayer
        self._layers: dict[tuple[str, str], ConfigLayer] = {}

    def set_layer(
        self,
        installation_id: str,
        layer_id: str,
        priority: int,
        values: dict,
    ) -> ConfigLayer:
        """Set or replace a configuration layer."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not layer_id:
            raise ValueError("layer_id is required")

        layer = ConfigLayer(layer_id=layer_id, priority=priority, values=dict(values))
        self._layers[(installation_id, layer_id)] = layer
        return layer

    def remove_layer(self, installation_id: str, layer_id: str) -> bool:
        key = (installation_id, layer_id)
        if key in self._layers:
            del self._layers[key]
            return True
        return False

    def get_value(self, installation_id: str, key: str, default: object = None) -> object:
        """Get a resolved config value (highest priority wins)."""
        layers = self._sorted_layers(installation_id)
        for layer in layers:
            if key in layer.values:
                return layer.values[key]
        return default

    def resolve(self, installation_id: str) -> dict:
        """Resolve all config values with priority layering."""
        layers = list(reversed(self._sorted_layers(installation_id)))
        result: dict = {}
        for layer in layers:
            result.update(layer.values)
        return result

    def get_layer(self, installation_id: str, layer_id: str) -> ConfigLayer:
        key = (installation_id, layer_id)
        layer = self._layers.get(key)
        if layer is None:
            raise KeyError(f"Layer {layer_id} not found")
        return layer

    def list_layers(self, installation_id: str) -> list[ConfigLayer]:
        """List layers sorted by priority (highest first)."""
        return self._sorted_layers(installation_id)

    def _sorted_layers(self, installation_id: str) -> list[ConfigLayer]:
        layers = [
            layer for (inst, _), layer in self._layers.items()
            if inst == installation_id
        ]
        return sorted(layers, key=lambda l: l.priority, reverse=True)
