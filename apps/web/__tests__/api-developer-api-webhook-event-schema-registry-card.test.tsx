import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookEventSchemaRegistryCard from "../src/components/api-developer-api-webhook-event-schema-registry-card";

const schemas = [
  { event_type: "push", version: "2.0", field_count: 5, required_count: 2, description: "Push event" },
  { event_type: "issue", version: "1.0", field_count: 3, required_count: 1, description: "Issue event" },
];

describe("APIDeveloperAPIWebhookEventSchemaRegistryCard", () => {
  it("shows schemas", () => {
    const { container } = render(<APIDeveloperAPIWebhookEventSchemaRegistryCard schemas={schemas} eventTypes={["push", "issue"]} appName="App" />);
    expect(container.textContent).toContain("Event Schema Registry");
    expect(container.textContent).toContain("2 event types");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("5 fields");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIWebhookEventSchemaRegistryCard schemas={[]} eventTypes={[]} appName="App" />);
    expect(container.textContent).toContain("No schemas registered");
  });
});
