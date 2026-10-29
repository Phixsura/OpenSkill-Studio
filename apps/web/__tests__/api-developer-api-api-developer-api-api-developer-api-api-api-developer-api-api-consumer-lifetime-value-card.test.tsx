import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiConsumerLifetimeValueCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-developer-api-api-consumer-lifetime-value-card";

const consumers = [{ consumer_id: "acme", ltv_cents: 240000, arpu_cents: 10000, plan: "enterprise", churn_risk: "low", months_active: 24 }];

describe("Card", () => {
  it("shows LTV", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiConsumerLifetimeValueCard consumers={consumers} totalMrrCents={50000} atRiskCount={2} appName="App" />);
    expect(container.textContent).toContain("Consumer LTV");
    expect(container.textContent).toContain("MRR: $500");
    expect(container.textContent).toContain("2 at risk");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("LTV: $2400");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiConsumerLifetimeValueCard consumers={[]} totalMrrCents={0} atRiskCount={0} appName="App" />);
    expect(container.textContent).toContain("No consumer data");
  });
});
