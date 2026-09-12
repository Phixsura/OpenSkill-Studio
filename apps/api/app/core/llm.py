"""LLM client abstraction — dual-provider (Anthropic + OpenAI), multimodal.

Includes retry with exponential backoff for transient errors (429, 500, timeouts).
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds


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
        user_prompt: str | list,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> LLMResponse:
        """Complete a prompt.

        user_prompt accepts:
        - str: plain text (backward-compatible)
        - list: content blocks for multimodal input, e.g.:
          [{"type": "text", "text": "..."}, {"type": "image", "source": {...}}]

        The Anthropic block format is canonical; providers translate as needed.
        """
        ...


class AnthropicClient(LLMClient):
    """Claude API client — supports text and vision (image content blocks)."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-5"):
        import anthropic

        self.client = anthropic.AsyncAnthropic(
            api_key=api_key,
            timeout=settings.eval_timeout_seconds,
        )
        self.model = model
        # Only retry on transient errors
        self._transient = (
            anthropic.APITimeoutError,
            anthropic.RateLimitError,
            anthropic.InternalServerError,
        )

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str | list,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> LLMResponse:
        # Retry with exponential backoff for transient errors
        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
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
            except self._transient as exc:
                last_exc = exc
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2**attempt)
                    logger.warning(
                        "llm_retry",
                        extra={"attempt": attempt + 1, "delay": delay, "error": str(exc)},
                    )
                    await asyncio.sleep(delay)
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("Max retries exceeded with no exception")


class OpenAIClient(LLMClient):
    """OpenAI API client — supports text and vision (image_url content blocks)."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=settings.eval_timeout_seconds,
        )
        self.model = model
        # Only retry on transient errors
        import openai

        self._transient = (
            openai.APITimeoutError,
            openai.RateLimitError,
            openai.InternalServerError,
        )

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str | list,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> LLMResponse:
        content = _to_openai_content(user_prompt) if isinstance(user_prompt, list) else user_prompt

        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": content},
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
            except self._transient as exc:
                last_exc = exc
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2**attempt)
                    logger.warning(
                        "llm_retry",
                        extra={"attempt": attempt + 1, "delay": delay, "error": str(exc)},
                    )
                    await asyncio.sleep(delay)
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("Max retries exceeded with no exception")


def _to_openai_content(blocks: list) -> list:
    """Convert Anthropic-style content blocks to OpenAI format.

    Anthropic: {"type": "image", "source": {"type": "base64", "media_type": "...", "data": "..."}}
    OpenAI:    {"type": "image_url", "image_url": {"url": "data:...;base64,..."}}
    """
    result = []
    for block in blocks:
        if block.get("type") == "text":
            result.append({"type": "text", "text": block["text"]})
        elif block.get("type") == "image":
            source = block.get("source", {})
            data_url = (
                f"data:{source.get('media_type', 'image/png')};base64,{source.get('data', '')}"
            )
            result.append({"type": "image_url", "image_url": {"url": data_url}})
        else:
            # Pass through unknown block types as text
            result.append({"type": "text", "text": str(block)})
    return result


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


# R67[6]: fallback rates for models absent from PRICING. default_model is an
# org-selectable free string — an unknown-but-served model previously costed
# $0, silently exempting the org from every budget while real provider spend
# accrued. Charging at the flagship tier is conservative for the platform:
# over-counting throttles earlier, never bills less than reality.
_FALLBACK_PRICES: dict[str, float] = {"input": 3.00, "output": 15.00}


def calculate_cost(response: LLMResponse) -> float:
    """Calculate USD cost from token counts."""
    prices = PRICING.get(response.provider, {}).get(response.model)
    if prices is None:
        logger.warning(
            "llm_cost_unknown_model provider=%s model=%s", response.provider, response.model
        )
        prices = _FALLBACK_PRICES
    input_cost = response.input_tokens * prices.get("input", 0) / 1_000_000
    output_cost = response.output_tokens * prices.get("output", 0) / 1_000_000
    return round(input_cost + output_cost, 6)
