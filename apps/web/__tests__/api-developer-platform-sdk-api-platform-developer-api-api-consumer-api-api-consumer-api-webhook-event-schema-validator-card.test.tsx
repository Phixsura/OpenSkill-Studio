import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-webhook-event-schema-validator-card";

describe("WebhookEventSchemaValidatorCard", () => {
  it("shows schemas", () => {
    const schemas = [{ id: "s1", eventType: "order.created", version: "1.0", fields: [{ name: "order_id", type: "string", required: true }] }];
    const { container } = render(<Card schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("Event Schemas");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("v1.0");
    expect(container.textContent).toContain("order_id: string");
  });
  it("shows empty", () => {
    const { container } = render(<Card schemas={[]} appName="App" />);
    expect(container.textContent).toContain("No schemas registered");
  });
});
