import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TimeoutCalculator } from "@/components/timeout-calculator";

describe("TimeoutCalculator", () => {
  it("renders", () => {
    const { container } = render(
      <TimeoutCalculator chainP99Ms={200} safetyMarginMs={40}
        recommendedTimeoutMs={240} currentBudgetMs={400} overBudget={false} depsInChain={3} />
    );
    expect(container.textContent).toContain("Timeout Calculator");
    expect(container.textContent).toContain("Within budget");
    expect(container.textContent).toContain("200ms");
    expect(container.textContent).toContain("240ms");
    expect(container.textContent).toContain("400ms");
    expect(container.textContent).toContain("3 deps");
  });
});
