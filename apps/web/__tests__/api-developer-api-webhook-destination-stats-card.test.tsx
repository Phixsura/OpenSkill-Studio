import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookDestinationStatsCard from "../src/components/api-developer-api-webhook-destination-stats-card";

const stats = [
  { destination: "https://good.com", total_delivered: 950, total_failed: 50, success_rate: 95, avg_latency_ms: 120 },
  { destination: "https://bad.com", total_delivered: 50, total_failed: 50, success_rate: 50, avg_latency_ms: 500 },
];

describe("APIDeveloperAPIWebhookDestinationStatsCard", () => {
  it("shows stats", () => {
    const { container } = render(<APIDeveloperAPIWebhookDestinationStatsCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("Destination Stats");
    expect(container.textContent).toContain("1 failing");
    expect(container.textContent).toContain("95%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIWebhookDestinationStatsCard stats={[]} appName="App" />);
    expect(container.textContent).toContain("No destination stats");
  });
});
