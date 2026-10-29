import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiConsumerErrorBudgetCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-consumer-error-budget-card";

const budgets = [
  { consumer_id: "acme", slo_pct: 99.9, budget_remaining_pct: 0.05, burn_rate: 0.5, exhausted: false, current_success_pct: 99.95 },
  { consumer_id: "beta", slo_pct: 99.0, budget_remaining_pct: 0, burn_rate: 5.0, exhausted: true, current_success_pct: 95.0 },
];

describe("Card", () => {
  it("shows consumer error budgets", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiConsumerErrorBudgetCard budgets={budgets} exhaustedCount={1} appName="App" />);
    expect(container.textContent).toContain("Consumer Error Budgets");
    expect(container.textContent).toContain("1 exhausted");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("0.05% remaining");
    expect(container.textContent).toContain("burn: 5x");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiConsumerErrorBudgetCard budgets={[]} exhaustedCount={0} appName="App" />);
    expect(container.textContent).toContain("No error budgets");
  });
});
