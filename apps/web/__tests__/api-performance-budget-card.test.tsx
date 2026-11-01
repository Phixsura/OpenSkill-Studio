import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIPerformanceBudgetCard from "../src/components/api-performance-budget-card";

const budgets = [
  { budget_id: "b1", metric: "response_time_ms", max_value: 200, current_value: 150, usage_pct: 75, within_budget: true, violations: 0 },
  { budget_id: "b2", metric: "payload_size_kb", max_value: 100, current_value: 150, usage_pct: 150, within_budget: false, violations: 3 },
];

describe("APIPerformanceBudgetCard", () => {
  it("renders header and over budget count", () => {
    const { container } = render(<APIPerformanceBudgetCard budgets={budgets} appName="App" />);
    expect(container.textContent).toContain("Perf Budgets");
    expect(container.textContent).toContain("1 over budget");
  });

  it("shows metrics and values", () => {
    const { container } = render(<APIPerformanceBudgetCard budgets={budgets} appName="App" />);
    expect(container.textContent).toContain("response_time_ms");
    expect(container.textContent).toContain("150 / 200");
  });

  it("shows empty state", () => {
    const { container } = render(<APIPerformanceBudgetCard budgets={[]} appName="App" />);
    expect(container.textContent).toContain("No performance budgets");
  });
});
