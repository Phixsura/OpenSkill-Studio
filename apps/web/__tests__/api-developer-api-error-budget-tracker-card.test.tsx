import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIErrorBudgetTrackerCard from "../src/components/api-developer-api-error-budget-tracker-card";

const budgets = [
  { endpoint: "/api/users", slo_target_pct: 99.9, current_success_pct: 99.0, budget_remaining_pct: 0, budget_exhausted: true },
  { endpoint: "/api/data", slo_target_pct: 99.0, current_success_pct: 99.5, budget_remaining_pct: 0.5, budget_exhausted: false },
];

describe("APIDeveloperAPIErrorBudgetTrackerCard", () => {
  it("shows budget data", () => {
    const { container } = render(<APIDeveloperAPIErrorBudgetTrackerCard budgets={budgets} appName="App" />);
    expect(container.textContent).toContain("Error Budget Tracker");
    expect(container.textContent).toContain("1 exhausted");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("SLO: 99.9%");
    expect(container.textContent).toContain("0.5% remaining");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIErrorBudgetTrackerCard budgets={[]} appName="App" />);
    expect(container.textContent).toContain("No error budgets configured");
  });
});
