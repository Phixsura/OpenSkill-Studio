import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-error-budget-tracker-card";

describe("ErrorBudgetTrackerCard", () => {
  it("shows budgets", () => {
    const budgets = [{ consumer_id: "c1", slo_target_pct: 99.9, budget_consumed: 45, budget_remaining_pct: 55, status: "warning" }];
    const { container } = render(<Card budgets={budgets} atRiskCount={1} appName="App" />);
    expect(container.textContent).toContain("Error Budgets");
    expect(container.textContent).toContain("1 at risk");
    expect(container.textContent).toContain("warning");
    expect(container.textContent).toContain("55% left");
  });
  it("shows empty", () => {
    const { container } = render(<Card budgets={[]} atRiskCount={0} appName="App" />);
    expect(container.textContent).toContain("No error budgets");
  });
});
