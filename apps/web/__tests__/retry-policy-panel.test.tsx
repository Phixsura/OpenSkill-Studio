import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RetryPolicyPanel } from "@/components/retry-policy-panel";

describe("RetryPolicyPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RetryPolicyPanel strategy="exponential" maxAttempts={3} baseMs={1000}
        budgetUsed={500} budgetTotal={1000} budgetPct={50} exhausted={false} />
    );
    expect(container.textContent).toContain("Retry Policy");
    expect(container.textContent).toContain("exponential");
    expect(container.textContent).toContain("max 3");
    expect(container.textContent).toContain("500/1000");
    expect(container.textContent).toContain("50%");
  });
});
