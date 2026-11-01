import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiConsumerBillingProfileCard from "../src/components/api-developer-api-api-developer-api-api-consumer-billing-profile-card";

const profiles = [
  { consumer_id: "acme", plan: "pro", current_spend_cents: 50000, monthly_budget_cents: 100000, budget_usage_pct: 50, over_budget: false },
  { consumer_id: "beta", plan: "starter", current_spend_cents: 1500, monthly_budget_cents: 1000, budget_usage_pct: 150, over_budget: true },
];

describe("APIDeveloperAPIApiDeveloperApiApiConsumerBillingProfileCard", () => {
  it("shows billing profiles", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiConsumerBillingProfileCard profiles={profiles} planBreakdown={{ pro: 1, starter: 1 }} overBudgetCount={1} appName="App" />);
    expect(container.textContent).toContain("Billing Profiles");
    expect(container.textContent).toContain("1 over budget");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("$500.00");
    expect(container.textContent).toContain("pro: 1");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiConsumerBillingProfileCard profiles={[]} planBreakdown={{}} overBudgetCount={0} appName="App" />);
    expect(container.textContent).toContain("No billing profiles");
  });
});
