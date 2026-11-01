import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-performance-budget-card";

describe("ConsumerApiPerformanceBudgetCard", () => {
  it("shows reports", () => {
    const reports = [{ path: "/api/users", withinBudget: false, score: 75, violations: [{ metric: "p95", budget: 200, actual: 350 }] }];
    const { container } = render(<Card reports={reports} appName="App" />);
    expect(container.textContent).toContain("Performance Budget");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("75%");
    expect(container.textContent).toContain("p95: 350ms");
  });
  it("shows empty", () => {
    const { container } = render(<Card reports={[]} appName="App" />);
    expect(container.textContent).toContain("No performance budgets");
  });
});
