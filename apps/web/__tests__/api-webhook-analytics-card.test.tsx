import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookAnalyticsCard from "../src/components/api-webhook-analytics-card";

const analytics = { total_sent: 10000, total_failed: 500, success_rate: 95.2, avg_latency_ms: 120.5, active_destinations: 5, top_event_type: "push" };

describe("APIWebhookAnalyticsCard", () => {
  it("shows analytics", () => {
    const { container } = render(<APIWebhookAnalyticsCard analytics={analytics} appName="App" />);
    expect(container.textContent).toContain("Webhook Analytics");
    expect(container.textContent).toContain("95.2%");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("120.5ms");
    expect(container.textContent).toContain("top: push");
  });
});
