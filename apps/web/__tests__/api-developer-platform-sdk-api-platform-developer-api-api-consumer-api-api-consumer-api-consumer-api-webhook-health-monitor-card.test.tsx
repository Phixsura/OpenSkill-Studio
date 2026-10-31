import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-webhook-health-monitor-card";

describe("ConsumerApiWebhookHealthMonitorCard", () => {
  it("shows summaries", () => {
    const summaries = [{ webhookId: "w1", status: "healthy", uptimePct: 99.5, avgResponseMs: 120, consecutiveFailures: 0, totalChecks: 100 }];
    const { container } = render(<Card summaries={summaries} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Webhook Health");
    expect(container.textContent).toContain("w1");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("99.5%");
  });
  it("shows empty", () => {
    const { container } = render(<Card summaries={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No webhooks monitored");
  });
});
