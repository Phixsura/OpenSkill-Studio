import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-event-transformer-card";

describe("WebhookEventTransformerCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", event_type: "order.created", rules: [{ rule_id: "r1", operation: "rename", source_field: "order_id" }], enabled: true }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Event Transformer");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("order_id");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No transform configs");
  });
});
