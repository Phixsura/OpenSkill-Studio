import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-webhook-delivery-analytics-card";

describe("WebhookDeliveryAnalyticsCard", () => {
  it("shows analytics", () => {
    const periods = [{ period: "2026-06-01", deliveries: 100, successRate: 95, avgMs: 120 }];
    const { container } = render(<Card webhookId="w1" totalDeliveries={1000} overallRate={96} avgMs={110} trend="improving" periods={periods} appName="App" />);
    expect(container.textContent).toContain("Delivery Analytics");
    expect(container.textContent).toContain("96%");
    expect(container.textContent).toContain("improving");
    expect(container.textContent).toContain("2026-06-01");
  });
  it("shows empty periods", () => {
    const { container } = render(<Card webhookId="w1" totalDeliveries={0} overallRate={100} avgMs={0} trend="stable" periods={[]} appName="App" />);
    expect(container.textContent).toContain("stable");
  });
});
