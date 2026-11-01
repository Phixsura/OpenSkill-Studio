import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiEndpointResponseTimeBudgetCard from "../src/components/api-developer-platform-sdk-api-endpoint-response-time-budget-card";

const budgets = [
  { endpoint: "/api/users", budget_ms: 200, p99_ms: 150, within_budget: true, headroom_pct: 25, violation_rate: 0 },
  { endpoint: "/api/search", budget_ms: 100, p99_ms: 250, within_budget: false, headroom_pct: -150, violation_rate: 80 },
];

describe("Card", () => {
  it("shows budgets", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiEndpointResponseTimeBudgetCard budgets={budgets} overBudgetCount={1} appName="App" />);
    expect(container.textContent).toContain("Response Time Budgets");
    expect(container.textContent).toContain("1 over budget");
    expect(container.textContent).toContain("p99: 150ms / 200ms");
    expect(container.textContent).toContain("headroom: 25%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiEndpointResponseTimeBudgetCard budgets={[]} overBudgetCount={0} appName="App" />);
    expect(container.textContent).toContain("No time budgets");
  });
});
