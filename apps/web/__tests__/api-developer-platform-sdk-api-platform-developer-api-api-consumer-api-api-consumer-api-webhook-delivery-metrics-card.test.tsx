import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-webhook-delivery-metrics-card";

describe("WebhookDeliveryMetricsCard", () => {
  it("shows metrics", () => {
    const metrics = [{ consumer_id: "c1", success_rate: 98.5, avg_latency_ms: 125, retry_rate: 5, total_deliveries: 10000 }];
    const { container } = render(<Card metrics={metrics} appName="App" />);
    expect(container.textContent).toContain("Delivery Metrics");
    expect(container.textContent).toContain("98.5%");
    expect(container.textContent).toContain("10,000 del");
  });
  it("shows empty", () => {
    const { container } = render(<Card metrics={[]} appName="App" />);
    expect(container.textContent).toContain("No delivery metrics");
  });
});
