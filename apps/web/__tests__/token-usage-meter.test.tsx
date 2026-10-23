import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TokenUsageMeter } from "@/components/token-usage-meter";

describe("TokenUsageMeter", () => {
  it("renders", () => {
    const { container } = render(
      <TokenUsageMeter totalTokens={5000} inputTokens={3000} outputTokens={2000}
        estimatedCost={0.039} budget={10000} pctUsed={50} exceeded={false} warning={false} />
    );
    expect(container.textContent).toContain("Token Usage");
    expect(container.textContent).toContain("$0.0390");
    expect(container.textContent).toContain("5,000 / 10,000");
    expect(container.textContent).toContain("3,000");
    expect(container.textContent).toContain("2,000");
  });
  it("exceeded", () => {
    const { container } = render(
      <TokenUsageMeter totalTokens={12000} inputTokens={8000} outputTokens={4000}
        estimatedCost={0.084} budget={10000} pctUsed={120} exceeded={true} warning={true} />
    );
    expect(container.textContent).toContain("⚠️ Token budget exceeded");
  });
});
