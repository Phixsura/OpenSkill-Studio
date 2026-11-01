import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-webhook-testing-card";

describe("ConsumerApiWebhookTestingCard", () => {
  it("shows tests", () => {
    const results = [{ id: "t1", eventType: "ping", status: 200, latencyMs: 45, success: true, testedAt: "12:00" }];
    const { container } = render(<Card results={results} standardEvents={["ping", "order.created"]} successRate={1.0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Webhook Testing");
    expect(container.textContent).toContain("ping");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("order.created");
  });
  it("shows empty", () => {
    const { container } = render(<Card results={[]} standardEvents={["ping"]} successRate={1.0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No tests run");
  });
});
