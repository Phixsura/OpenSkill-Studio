import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-webhook-log-card";

describe("ConsumerWebhookLogCard", () => {
  it("shows logs and stats", () => {
    const logs = [{ id: "l1", eventType: "order.created", status: 200, success: true, responseTimeMs: 50, attempt: 1, timestamp: "12:00" }];
    const { container } = render(<Card logs={logs} consumerId="c1" failureRate={0.05} avgResponseMs={75} appName="App" />);
    expect(container.textContent).toContain("Webhook Log");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("5.0%");
    expect(container.textContent).toContain("75ms");
  });
  it("shows empty", () => {
    const { container } = render(<Card logs={[]} consumerId="c1" failureRate={0} avgResponseMs={0} appName="App" />);
    expect(container.textContent).toContain("No webhook logs");
  });
});
