import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AIIntegrationPanel } from "@/components/ai-integration-panel";

const models = [
  { modelId: "claude-sonnet-5", provider: "anthropic", name: "Claude Sonnet 5", maxTokens: 200000, costPer1kInput: 0.3, costPer1kOutput: 1.5 },
  { modelId: "gpt-4o-mini", provider: "openai", name: "GPT-4o Mini", maxTokens: 128000, costPer1kInput: 0.015, costPer1kOutput: 0.06 },
];
const usage = [
  { modelId: "claude-sonnet-5", requests: 100, inputTokens: 500000, outputTokens: 200000, totalCostCents: 450, cachedResponses: 20 },
];

describe("AIIntegrationPanel", () => {
  it("renders models and usage", () => {
    const { container } = render(<AIIntegrationPanel models={models} usage={usage} totalCostCents={450} />);
    expect(container.textContent).toContain("Claude Sonnet 5");
    expect(container.textContent).toContain("GPT-4o Mini");
    expect(container.textContent).toContain("100 reqs");
    expect(container.textContent).toContain("$4.50");
  });
});
