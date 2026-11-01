import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-webhook-payload-schema-card";

describe("PayloadSchemaCard", () => {
  it("shows schemas", () => {
    const schemas = [{ schema_id: "s1", event_type: "order.created", version: "1.0", field_count: 5, required_count: 3 }];
    const { container } = render(<Card schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("Payload Schemas");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("v1.0");
    expect(container.textContent).toContain("3/5 required");
  });
  it("shows empty", () => {
    const { container } = render(<Card schemas={[]} appName="App" />);
    expect(container.textContent).toContain("No schemas registered");
  });
});
