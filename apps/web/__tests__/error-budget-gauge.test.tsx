import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorBudgetGauge } from "@/components/error-budget-gauge";

describe("ErrorBudgetGauge", () => {
  it("renders healthy", () => {
    const { container } = render(
      <ErrorBudgetGauge budgetPct={75} burnRate={0.8} sloTarget={99.9} recommendation="OK: Budget healthy" />
    );
    expect(container.textContent).toContain("75%");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("0.8x");
    expect(container.textContent).toContain("OK");
  });
  it("renders exhausted", () => {
    const { container } = render(
      <ErrorBudgetGauge budgetPct={0} burnRate={3} sloTarget={99.9} recommendation="FREEZE: Budget exhausted" />
    );
    expect(container.textContent).toContain("0%");
    expect(container.textContent).toContain("FREEZE");
  });
});
