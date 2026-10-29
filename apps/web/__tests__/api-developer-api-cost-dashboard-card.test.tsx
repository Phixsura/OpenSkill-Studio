import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPICostDashboardCard from "../src/components/api-developer-api-cost-dashboard-card";

const cost = { total_cost: 1500, budget_limit: 2000, budget_used_pct: 75, projected_monthly: 1800, cost_trend: "increasing", over_budget: false, currency: "USD" };

describe("APIDeveloperAPICostDashboardCard", () => {
  it("shows cost metrics", () => {
    const { container } = render(<APIDeveloperAPICostDashboardCard cost={cost} appName="App" />);
    expect(container.textContent).toContain("Cost Dashboard");
    expect(container.textContent).toContain("USD 1500.00");
    expect(container.textContent).toContain("75%");
    expect(container.textContent).toContain("increasing");
  });
});
