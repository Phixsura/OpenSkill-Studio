import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiWebhookEventTypeRegistryCard from "../src/components/api-developer-api-api-developer-api-api-webhook-event-type-registry-card";

const types = [
  { event_type: "order.created", description: "Order was created", schema_version: "2.0", category: "resource", deprecated: false },
  { event_type: "old.event", description: "Old", schema_version: "1.0", category: "system", deprecated: true },
];

describe("Card", () => {
  it("shows event types", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookEventTypeRegistryCard types={types} categoryCounts={{ resource: 1, system: 1 }} appName="App" />);
    expect(container.textContent).toContain("Event Types");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("resource: 1");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookEventTypeRegistryCard types={[]} categoryCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No event types");
  });
});
