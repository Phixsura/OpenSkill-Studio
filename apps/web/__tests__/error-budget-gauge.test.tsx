import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorBudgetGauge } from "@/components/error-budget-gauge";

describe("ErrorBudgetGauge", () => {
  it("renders healthy budget", () => {
    const { container } = render(
      <ErrorBudgetGauge sloDisplay="99.9%" consumedPct={10} remainingPct={90}
        burnRateDisplay="0.2x" status="healthy" budgetTotal={1000} budgetConsumed={100} />
    );
    expect(container.textContent).toContain("Error Budget");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("0.2x");
    expect(container.textContent).toContain("100");
  });
});
