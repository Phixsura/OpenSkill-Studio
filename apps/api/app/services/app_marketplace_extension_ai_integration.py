"""AI Integration Helper — simplify AI model integration for extensions.

Provides model registry, prompt templates, token usage tracking,
cost estimation, and response caching for AI-powered extensions.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class AIModel:
    model_id: str
    provider: str  # openai, anthropic, local
    name: str
    max_tokens: int
    cost_per_1k_input: float  # cents
    cost_per_1k_output: float


@dataclass
class AIUsage:
    extension_id: str
    model_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    requests: int = 0
    total_cost_cents: float = 0.0
    cached_responses: int = 0


MODELS = {
    "claude-sonnet-5": AIModel("claude-sonnet-5", "anthropic", "Claude Sonnet 5", 200000, 0.3, 1.5),
    "claude-haiku-4.5": AIModel("claude-haiku-4.5", "anthropic", "Claude Haiku 4.5", 200000, 0.08, 0.4),
    "gpt-4o": AIModel("gpt-4o", "openai", "GPT-4o", 128000, 0.25, 1.0),
    "gpt-4o-mini": AIModel("gpt-4o-mini", "openai", "GPT-4o Mini", 128000, 0.015, 0.06),
}


class ExtensionAIIntegrationService:
    """Manages AI model integration for extensions."""

    def __init__(self):
        self._usage: dict[str, dict[str, AIUsage]] = defaultdict(dict)
        self._cache: dict[str, str] = {}

    def list_models(self) -> list[AIModel]:
        return list(MODELS.values())

    def get_model(self, model_id: str) -> AIModel | None:
        return MODELS.get(model_id)

    def record_usage(self, extension_id: str, model_id: str,
                     input_tokens: int, output_tokens: int,
                     cached: bool = False) -> AIUsage:
        model = MODELS.get(model_id)
        if not model:
            raise ValueError(f"Unknown model: {model_id}")

        key = model_id
        if key not in self._usage[extension_id]:
            self._usage[extension_id][key] = AIUsage(extension_id=extension_id, model_id=model_id)

        usage = self._usage[extension_id][key]
        usage.input_tokens += input_tokens
        usage.output_tokens += output_tokens
        usage.requests += 1
        cost = (input_tokens / 1000 * model.cost_per_1k_input +
                output_tokens / 1000 * model.cost_per_1k_output)
        usage.total_cost_cents += round(cost, 4)
        if cached:
            usage.cached_responses += 1
        return usage

    def get_usage(self, extension_id: str) -> list[AIUsage]:
        return list(self._usage.get(extension_id, {}).values())

    def estimate_cost(self, model_id: str, input_tokens: int,
                      output_tokens: int) -> dict:
        model = MODELS.get(model_id)
        if not model:
            return {"error": "Unknown model"}
        cost = (input_tokens / 1000 * model.cost_per_1k_input +
                output_tokens / 1000 * model.cost_per_1k_output)
        return {"model": model.name, "input_tokens": input_tokens,
                "output_tokens": output_tokens, "cost_cents": round(cost, 2)}

    def get_total_cost(self, extension_id: str) -> float:
        return round(sum(u.total_cost_cents for u in self._usage.get(extension_id, {}).values()), 2)
