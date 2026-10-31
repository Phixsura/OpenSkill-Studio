import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-error-budget-dashboard-card";

describe("ErrorBudgetDashboardCard", () => {
  it("shows budgets", () => {
    const entries = [{ endpoint: "/api/users", sloTarget: 99.9, remaining: 50, burnRate: 1.5 }];
    const { container } = render(<Card entries={entries} overallPct={50} atRisk={0} exhausted={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Error Budget");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("SLO: 99.9%");
  });
  it("shows empty", () => {
    const { container } = render(<Card entries={[]} overallPct={100} atRisk={0} exhausted={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No error budgets");
  });
});
