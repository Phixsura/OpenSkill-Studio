import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-error-budget-card";

describe("ErrorBudgetCard", () => {
  it("shows budgets", () => {
    const budgets = [{ endpoint: "/api/users", slo_target_pct: 99.9, budget_consumed_pct: 50, budget_remaining: 5, status: "warning" }];
    const { container } = render(<Card budgets={budgets} alertCount={1} appName="App" />);
    expect(container.textContent).toContain("Error Budgets");
    expect(container.textContent).toContain("1 alert");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("warning");
  });
  it("shows empty", () => {
    const { container } = render(<Card budgets={[]} alertCount={0} appName="App" />);
    expect(container.textContent).toContain("No error budgets");
  });
});
