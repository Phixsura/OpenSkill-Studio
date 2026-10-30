import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-webhook-event-type-registry-card";

describe("WebhookEventTypeRegistryCard", () => {
  it("shows types", () => {
    const types = [{ event_type: "order.created", category: "order", deprecated: false, subscriber_count: 15 }];
    const { container } = render(<Card types={types} activeCount={1} deprecatedCount={0} appName="App" />);
    expect(container.textContent).toContain("Event Type Registry");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("15 subs");
  });
  it("shows deprecated count", () => {
    const { container } = render(<Card types={[]} activeCount={0} deprecatedCount={3} appName="App" />);
    expect(container.textContent).toContain("3 deprecated");
  });
});
