import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ErrorBudgetCard from "../src/components/error-budget-card";

const budgets = [
  {
    service_id: "api",
    slo_target: 99.9,
    budget_total: 99,
    error_count: 30,
    budget_remaining: 69,
    budget_consumed_pct: 30.3,
    is_exhausted: false,
  },
  {
    service_id: "payments",
    slo_target: 99.99,
    budget_total: 10,
    error_count: 10,
    budget_remaining: 0,
    budget_consumed_pct: 100,
    is_exhausted: true,
  },
];

describe("ErrorBudgetCard", () => {
  it("renders header and service count", () => {
    const { container } = render(<ErrorBudgetCard budgets={budgets} appName="App" />);
    expect(container.textContent).toContain("Error Budgets");
    expect(container.textContent).toContain("2 services");
  });

  it("shows exhausted count", () => {
    const { container } = render(<ErrorBudgetCard budgets={budgets} appName="App" />);
    expect(container.textContent).toContain("1 exhausted");
  });

  it("shows SLO targets", () => {
    const { container } = render(<ErrorBudgetCard budgets={budgets} appName="App" />);
    expect(container.textContent).toContain("SLO 99.9%");
    expect(container.textContent).toContain("SLO 99.99%");
  });

  it("shows consumed and remaining", () => {
    const { container } = render(<ErrorBudgetCard budgets={budgets} appName="App" />);
    expect(container.textContent).toContain("30.3% consumed");
    expect(container.textContent).toContain("69 remaining");
  });

  it("shows empty state", () => {
    const { container } = render(<ErrorBudgetCard budgets={[]} appName="App" />);
    expect(container.textContent).toContain("No error budgets");
  });
});
