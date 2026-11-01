import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-retry-budget-card";

describe("RetryBudgetCard", () => {
  it("shows budgets", () => {
    const budgets = [{ consumer_id: "c1", budget_per_minute: 100, used: 45, remaining: 55, usage_pct: 45, total_exhausted: 2 }];
    const { container } = render(<Card budgets={budgets} appName="App" />);
    expect(container.textContent).toContain("Retry Budgets");
    expect(container.textContent).toContain("45/100/min");
  });
  it("shows empty", () => {
    const { container } = render(<Card budgets={[]} appName="App" />);
    expect(container.textContent).toContain("No retry budgets");
  });
});
