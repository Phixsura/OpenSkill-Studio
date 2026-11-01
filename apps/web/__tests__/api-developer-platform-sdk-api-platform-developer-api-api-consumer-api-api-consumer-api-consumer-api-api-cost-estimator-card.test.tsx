import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-cost-estimator-card";

describe("ConsumerApiCostEstimatorCard", () => {
  it("shows estimate", () => {
    const { container } = render(<Card consumerId="c1" period="2026-06" projectedRequests={15000} baseCostCents={100} overageCostCents={10} totalCostCents={110} savingsCents={20} tierName="basic" appName="App" />);
    expect(container.textContent).toContain("Cost Estimator");
    expect(container.textContent).toContain("$1.10");
    expect(container.textContent).toContain("$1.00");
    expect(container.textContent).toContain("$0.10");
    expect(container.textContent).toContain("save $0.20");
  });
  it("shows no overage", () => {
    const { container } = render(<Card consumerId="c1" period="2026-06" projectedRequests={5000} baseCostCents={100} overageCostCents={0} totalCostCents={100} savingsCents={0} tierName="pro" appName="App" />);
    expect(container.textContent).toContain("$1.00");
    expect(container.textContent).not.toContain("save");
  });
});
