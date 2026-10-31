import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiConsumerWebhookStatsCard from "../src/components/api-developer-platform-sdk-api-developer-api-consumer-webhook-stats-card";

const stats = [{ consumer_id: "acme", success_rate: 99.5, health_status: "excellent", total_deliveries: 50000, avg_latency_ms: 45, retry_rate: 0.5 }];

describe("Card", () => {
  it("shows webhook stats", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiConsumerWebhookStatsCard stats={stats} healthBreakdown={{ excellent: 5, poor: 1 }} appName="App" />);
    expect(container.textContent).toContain("Consumer Webhook Stats");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("excellent: 5");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiConsumerWebhookStatsCard stats={[]} healthBreakdown={{}} appName="App" />);
    expect(container.textContent).toContain("No webhook stats");
  });
});
