"""LLM client abstraction — dual-provider (Anthropic + OpenAI)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.config import settings


@dataclass
class LLMResponse:
    content: str
    input_tokens: int
    output_tokens: int
    model: str
    provider: str


class LLMClient(ABC):
    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> LLMResponse: ...


class AnthropicClient(LLMClient):
    """Claude API client."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-5"):
        import anthropic

        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> LLMResponse:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return LLMResponse(
            content=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model=self.model,
            provider="anthropic",
        )


class OpenAIClient(LLMClient):
    """OpenAI API client."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
            model=self.model,
            provider="openai",
        )


def create_llm_client(model: str | None = None) -> LLMClient:
    """Factory: create LLM client from settings.

    `model` overrides the global default (per-org default_model setting).
    """
    resolved = model or settings.llm_model
    if settings.llm_provider == "anthropic":
        return AnthropicClient(settings.anthropic_api_key, resolved)
    elif settings.llm_provider == "openai":
        return OpenAIClient(settings.openai_api_key, resolved)
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


# ── Pricing (per 1M tokens, USD) ─────────────────────────

PRICING: dict[str, dict[str, dict[str, float]]] = {
    "anthropic": {
        "claude-sonnet-5": {"input": 3.00, "output": 15.00},
        "claude-haiku-4-5": {"input": 0.80, "output": 4.00},
    },
    "openai": {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    },
}


def calculate_cost(response: LLMResponse) -> float:
    """Calculate USD cost from token counts."""
    prices = PRICING.get(response.provider, {}).get(response.model, {})
    input_cost = response.input_tokens * prices.get("input", 0) / 1_000_000
    output_cost = response.output_tokens * prices.get("output", 0) / 1_000_000
    return round(input_cost + output_cost, 6)
