import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiPerformanceBudgetCard from "../src/components/api-developer-api-api-performance-budget-card";

const budgets = [
  { endpoint: "/api/users", max_latency_ms: 200, actual_latency_ms: 150, max_response_bytes: 51200, actual_response_bytes: 30000, within_budget: true, violation_count: 0 },
  { endpoint: "/api/heavy", max_latency_ms: 100, actual_latency_ms: 300, max_response_bytes: 10240, actual_response_bytes: 50000, within_budget: false, violation_count: 5 },
];

describe("APIDeveloperAPIApiPerformanceBudgetCard", () => {
  it("shows budgets", () => {
    const { container } = render(<APIDeveloperAPIApiPerformanceBudgetCard budgets={budgets} violationCount={1} appName="App" />);
    expect(container.textContent).toContain("Performance Budgets");
    expect(container.textContent).toContain("1 over budget");
    expect(container.textContent).toContain("150/200ms");
    expect(container.textContent).toContain("300/100ms");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiPerformanceBudgetCard budgets={[]} violationCount={0} appName="App" />);
    expect(container.textContent).toContain("No performance budgets");
  });
});
