import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-webhook-log-card";

describe("WebhookLogCard", () => {
  it("shows log", () => {
    const entries = [{ log_id: "l1", consumer_id: "c1", event_type: "order.created", status_code: 200, duration_ms: 42, success: true }];
    const stats = { total: 100, success: 95, failed: 5, success_rate: 95, avg_duration_ms: 50 };
    const { container } = render(<Card entries={entries} stats={stats} appName="App" />);
    expect(container.textContent).toContain("Webhook Log");
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("100");
  });
  it("shows empty stats", () => {
    const stats = { total: 0, success: 0, failed: 0, success_rate: 0, avg_duration_ms: 0 };
    const { container } = render(<Card entries={[]} stats={stats} appName="App" />);
    expect(container.textContent).toContain("Webhook Log");
  });
});
