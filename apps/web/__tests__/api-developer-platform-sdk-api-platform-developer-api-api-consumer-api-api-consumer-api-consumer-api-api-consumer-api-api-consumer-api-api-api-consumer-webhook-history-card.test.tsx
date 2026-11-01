import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-webhook-history-card";

describe("ConsumerWebhookHistoryCard", () => {
  it("shows deliveries", () => {
    const deliveries = [{ id: "d1", eventType: "order.created", status: 200, success: true, latencyMs: 50, timestamp: "12:00" }];
    const summary = { total: 100, successful: 95, failed: 5, avgMs: 75, successRate: 95 };
    const { container } = render(<Card deliveries={deliveries} summary={summary} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Webhook History");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("95%");
  });
  it("shows empty", () => {
    const summary = { total: 0, successful: 0, failed: 0, avgMs: 0, successRate: 100 };
    const { container } = render(<Card deliveries={[]} summary={summary} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No deliveries");
  });
});
