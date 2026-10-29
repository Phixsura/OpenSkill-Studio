import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiConsumerWebhookHealthReportCard from "../src/components/api-developer-platform-sdk-api-consumer-webhook-health-report-card";

const reports = [
  { consumer_id: "acme", success_rate: 99.5, health_grade: "A", total_deliveries: 50000, avg_latency_ms: 45 },
  { consumer_id: "beta", success_rate: 85, health_grade: "D", total_deliveries: 1000, avg_latency_ms: 500 },
];

describe("Card", () => {
  it("shows consumer health", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiConsumerWebhookHealthReportCard reports={reports} unhealthyCount={1} appName="App" />);
    expect(container.textContent).toContain("Consumer Webhook Health");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("99.5%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiConsumerWebhookHealthReportCard reports={[]} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("No health data");
  });
});
