import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookPayloadSchemaCard from "../src/components/api-webhook-payload-schema-card";

const schemas = [
  { event_type: "push", required_count: 3, optional_count: 1, pass_rate: 99.5, validations: 200 },
  { event_type: "issue", required_count: 2, optional_count: 2, pass_rate: 85.0, validations: 100 },
];

describe("APIWebhookPayloadSchemaCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIWebhookPayloadSchemaCard schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("Payload Schemas");
    expect(container.textContent).toContain("2 schemas");
  });

  it("shows event types and field counts", () => {
    const { container } = render(<APIWebhookPayloadSchemaCard schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("3 required");
    expect(container.textContent).toContain("99.5%");
  });

  it("shows empty state", () => {
    const { container } = render(<APIWebhookPayloadSchemaCard schemas={[]} appName="App" />);
    expect(container.textContent).toContain("No payload schemas");
  });
});
