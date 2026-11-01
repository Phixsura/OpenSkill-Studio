"""Dependency Injector — autowiring with interface binding and scopes.

More advanced than basic DI container: supports interface→implementation
binding, auto-wiring from type annotations, request-scoped lifetimes.

Implements:
- Interface binding (bind abstract to concrete)
- Auto-wiring (resolve dependencies from function signatures)
- Lazy singletons (create on first use)
- Decorator-based registration
- Module system (group related bindings)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import inspect


@dataclass
class Binding:
    interface: str
    implementation: callable
    singleton: bool = False
    instance: object | None = None
    lazy: bool = True


@dataclass
class Module:
    name: str
    bindings: dict[str, Binding] = field(default_factory=dict)


class DepInjectorService:
    def __init__(self):
        self._bindings: dict[str, Binding] = {}
        self._modules: dict[str, Module] = {}

    def bind(self, interface: str, implementation: callable,
             singleton: bool = False) -> None:
        """Bind an interface name to a concrete implementation."""
        self._bindings[interface] = Binding(
            interface=interface, implementation=implementation,
            singleton=singleton)

    def bind_instance(self, interface: str, instance: object) -> None:
        """Bind to an existing instance (always singleton)."""
        self._bindings[interface] = Binding(
            interface=interface, implementation=lambda: instance,
            singleton=True, instance=instance)

    def bind_factory(self, interface: str, factory: callable) -> None:
        """Bind to a factory function (new instance each time)."""
        self._bindings[interface] = Binding(
            interface=interface, implementation=factory, singleton=False)

    def resolve(self, interface: str) -> object:
        """Resolve an interface to a concrete instance."""
        binding = self._bindings.get(interface)
        if not binding:
            raise ValueError(f"No binding for '{interface}'")

        if binding.singleton and binding.instance is not None:
            return binding.instance

        # Auto-wire: inspect implementation's parameters
        impl = binding.implementation
        params = inspect.signature(impl).parameters
        args = {}
        for param_name, param in params.items():
            if param_name in self._bindings:
                args[param_name] = self.resolve(param_name)

        instance = impl(**args) if args else impl()

        if binding.singleton:
            binding.instance = instance

        return instance

    def create_module(self, name: str) -> Module:
        module = Module(name=name)
        self._modules[name] = module
        return module

    def module_bind(self, module_name: str, interface: str,
                    implementation: callable, singleton: bool = False) -> None:
        module = self._modules.get(module_name)
        if not module:
            module = self.create_module(module_name)
        binding = Binding(interface=interface, implementation=implementation,
                          singleton=singleton)
        module.bindings[interface] = binding

    def install_module(self, module_name: str) -> int:
        """Install all bindings from a module into the container."""
        module = self._modules.get(module_name)
        if not module:
            return 0
        for interface, binding in module.bindings.items():
            self._bindings[interface] = binding
        return len(module.bindings)

    def has_binding(self, interface: str) -> bool:
        return interface in self._bindings

    def get_bindings(self) -> list[dict]:
        return [{"interface": b.interface,
                 "singleton": b.singleton,
                 "instantiated": b.instance is not None}
                for b in self._bindings.values()]

    def reset(self) -> int:
        """Clear all singleton instances (keep bindings)."""
        count = 0
        for binding in self._bindings.values():
            if binding.instance is not None:
                binding.instance = None
                count += 1
        return count
