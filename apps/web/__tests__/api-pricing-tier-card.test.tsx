import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIPricingTierCard from "../src/components/api-pricing-tier-card";

const tiers = [
  { tier_id: "free", name: "Free", price_monthly: 0, features: ["basic_api"], rate_limit: 60 },
  { tier_id: "pro", name: "Pro", price_monthly: 49.99, features: ["basic_api", "webhooks", "analytics", "sso", "support"], rate_limit: 5000 },
];

describe("APIPricingTierCard", () => {
  it("renders header and tier count", () => {
    const { container } = render(<APIPricingTierCard tiers={tiers} appName="App" />);
    expect(container.textContent).toContain("Pricing Tiers");
    expect(container.textContent).toContain("2 tiers");
  });

  it("shows names and prices", () => {
    const { container } = render(<APIPricingTierCard tiers={tiers} appName="App" />);
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$0/mo");
    expect(container.textContent).toContain("$49.99/mo");
  });

  it("shows features and rate limit", () => {
    const { container } = render(<APIPricingTierCard tiers={tiers} appName="App" />);
    expect(container.textContent).toContain("webhooks");
    expect(container.textContent).toContain("5,000/min");
    expect(container.textContent).toContain("+1");
  });

  it("shows empty state", () => {
    const { container } = render(<APIPricingTierCard tiers={[]} appName="App" />);
    expect(container.textContent).toContain("No pricing tiers");
  });
});
