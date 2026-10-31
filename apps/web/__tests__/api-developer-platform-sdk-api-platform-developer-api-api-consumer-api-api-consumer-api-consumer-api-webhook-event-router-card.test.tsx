import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-webhook-event-router-card";

describe("ConsumerApiWebhookEventRouterCard", () => {
  it("shows rules", () => {
    const rules = [{ id: "r1", pattern: "order.*", webhookUrl: "https://hook.example.com/orders", priority: 10, active: true }];
    const { container } = render(<Card rules={rules} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Event Router");
    expect(container.textContent).toContain("order.*");
    expect(container.textContent).toContain("hook.example.com");
    expect(container.textContent).toContain("P10");
  });
  it("shows empty", () => {
    const { container } = render(<Card rules={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No routing rules");
  });
});
