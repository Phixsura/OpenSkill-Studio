import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrBudgetDashboard } from "@/components/err-budget-dashboard";

describe("ErrBudgetDashboard", () => {
  it("renders dashboard", () => {
    const { container } = render(
      <ErrBudgetDashboard totalSlos={3} exhausted={1} avgRemainingPct={60} status="critical"
        budgets={[
          { name: "Uptime", target: 99.9, actual: 99.95, consumedPct: 0, remainingPct: 100, exhausted: false },
          { name: "Latency", target: 99.0, actual: 98.5, consumedPct: 50, remainingPct: 50, exhausted: false },
          { name: "Errors", target: 99.9, actual: 99.7, consumedPct: 200, remainingPct: 0, exhausted: true },
        ]} />
    );
    expect(container.textContent).toContain("Error Budgets");
    expect(container.textContent).toContain("3 SLOs");
    expect(container.textContent).toContain("1 exhausted");
    expect(container.textContent).toContain("Uptime");
    expect(container.textContent).toContain("100% budget left");
    expect(container.textContent).toContain("Errors");
  });
});
