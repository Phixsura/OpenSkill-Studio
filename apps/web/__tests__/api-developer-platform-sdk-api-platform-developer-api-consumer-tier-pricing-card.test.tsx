import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-tier-pricing-card";

describe("TierPricingCard", () => {
  it("shows tiers", () => {
    const tiers = [{ tier_id: "pro", name: "Pro", monthly_limit: 10000, base_price_cents: 4999, price_per_request_cents: 0.1 }];
    const { container } = render(<Card tiers={tiers} appName="App" />);
    expect(container.textContent).toContain("Tier Pricing");
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("$49.99/mo");
    expect(container.textContent).toContain("10,000 requests");
  });
  it("shows empty", () => {
    const { container } = render(<Card tiers={[]} appName="App" />);
    expect(container.textContent).toContain("No pricing tiers");
  });
});
