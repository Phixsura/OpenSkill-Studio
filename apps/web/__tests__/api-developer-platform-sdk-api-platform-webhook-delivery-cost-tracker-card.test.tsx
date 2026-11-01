import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformWebhookDeliveryCostTrackerCard from "../src/components/api-developer-platform-sdk-api-platform-webhook-delivery-cost-tracker-card";

const costs = [{ destination: "https://api.example.com", total_deliveries: 50000, total_cost_cents: 25000, avg_cost_cents: 0.5, retry_cost_pct: 8 }];

describe("Card", () => {
  it("shows delivery costs", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformWebhookDeliveryCostTrackerCard costs={costs} totalCostCents={25000} appName="App" />);
    expect(container.textContent).toContain("Delivery Costs");
    expect(container.textContent).toContain("$250.00");
    expect(container.textContent).toContain("50,000 del");
    expect(container.textContent).toContain("8% retries");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformWebhookDeliveryCostTrackerCard costs={[]} totalCostCents={0} appName="App" />);
    expect(container.textContent).toContain("No cost data");
  });
});
