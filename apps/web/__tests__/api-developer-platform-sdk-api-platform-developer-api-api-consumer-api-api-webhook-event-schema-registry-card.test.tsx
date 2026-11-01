import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-event-schema-registry-card";

describe("EventSchemaRegistryCard", () => {
  it("shows schemas", () => {
    const schemas = [{ event_type: "order.created", version: "v1", field_count: 5, required_count: 3 }];
    const { container } = render(<Card schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("Event Schema Registry");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("3/5 req");
  });
  it("shows empty", () => {
    const { container } = render(<Card schemas={[]} appName="App" />);
    expect(container.textContent).toContain("No event schemas");
  });
});
