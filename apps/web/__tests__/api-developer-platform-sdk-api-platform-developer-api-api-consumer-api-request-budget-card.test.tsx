import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-request-budget-card";

describe("RequestBudgetCard", () => {
  it("shows budgets", () => {
    const budgets = [{ consumer_id: "c1", period: "2024-01", allocated: 10000, used: 8500, remaining: 1500, usage_pct: 85, rollover: 0 }];
    const { container } = render(<Card budgets={budgets} nearExhaustionCount={1} appName="App" />);
    expect(container.textContent).toContain("Request Budgets");
    expect(container.textContent).toContain("1 near limit");
    expect(container.textContent).toContain("8,500/10,000");
  });
  it("shows empty", () => {
    const { container } = render(<Card budgets={[]} nearExhaustionCount={0} appName="App" />);
    expect(container.textContent).toContain("No budgets");
  });
});
