import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiWebhookDeliveryMetricsAggregatorCard from "../src/components/api-developer-api-api-developer-api-api-webhook-delivery-metrics-aggregator-card";

const metrics = [{ period: "2025-01", total_deliveries: 50000, success_rate: 99.5, retry_rate: 0.8, avg_latency_ms: 45 }];

describe("Card", () => {
  it("shows delivery metrics", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookDeliveryMetricsAggregatorCard metrics={metrics} appName="App" />);
    expect(container.textContent).toContain("Delivery Metrics");
    expect(container.textContent).toContain("2025-01");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("50,000 total");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookDeliveryMetricsAggregatorCard metrics={[]} appName="App" />);
    expect(container.textContent).toContain("No delivery metrics");
  });
});
