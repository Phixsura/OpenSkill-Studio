import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookEventSchemaRegistryCard from "../src/components/api-webhook-event-schema-registry-card";

const schemas = [
  { event_type: "push", version: "2.0", field_count: 5, deprecated: false },
  { event_type: "push", version: "1.0", field_count: 3, deprecated: true },
];

describe("APIWebhookEventSchemaRegistryCard", () => {
  it("shows schemas", () => {
    const { container } = render(<APIWebhookEventSchemaRegistryCard schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("Schema Registry");
    expect(container.textContent).toContain("1 deprecated");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("v2.0");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookEventSchemaRegistryCard schemas={[]} appName="App" />);
    expect(container.textContent).toContain("No schemas registered");
  });
});
