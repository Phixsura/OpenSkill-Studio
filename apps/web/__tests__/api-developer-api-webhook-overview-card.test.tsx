import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookOverviewCard from "../src/components/api-developer-api-webhook-overview-card";

const overview = { total_events_emitted: 100000, total_deliveries: 95000, total_destinations: 25, total_subscriptions: 50, success_rate: 99.5, avg_delivery_ms: 120, circuit_breakers_open: 0, dead_letters: 5, retry_rate: 2.5, idempotency_dedup_count: 100, active_filters: 10 };

describe("APIDeveloperAPIWebhookOverviewCard", () => {
  it("shows complete overview", () => {
    const { container } = render(<APIDeveloperAPIWebhookOverviewCard overview={overview} appName="App" />);
    expect(container.textContent).toContain("Webhook Overview");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("100,000");
    expect(container.textContent).toContain("95,000");
    expect(container.textContent).toContain("120ms");
  });
});
