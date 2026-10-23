import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorBudgetGauge } from "@/components/error-budget-gauge";

describe("ErrorBudgetGauge", () => {
  it("renders healthy", () => {
    const { container } = render(
      <ErrorBudgetGauge sloTarget={99.9} actualSuccessRate={99.95} budgetPctUsed={50}
        budgetRemaining={50} status="ok" estimatedDaysRemaining={30} />
    );
    expect(container.textContent).toContain("Error Budget");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("ok");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("30d");
  });
  it("renders exhausted", () => {
    const { container } = render(
      <ErrorBudgetGauge sloTarget={99.9} actualSuccessRate={99.7} budgetPctUsed={120}
        budgetRemaining={0} status="exhausted" estimatedDaysRemaining={0} />
    );
    expect(container.textContent).toContain("exhausted");
  });
});
