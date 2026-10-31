import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookPayloadInspectorCard from "../src/components/api-developer-api-webhook-payload-inspector-card";

const inspections = [
  { inspection_id: "i1", event_type: "push", payload_size_bytes: 512, field_count: 5, has_nested: true, validation_errors: [] },
  { inspection_id: "i2", event_type: "issue", payload_size_bytes: 2048, field_count: 3, has_nested: false, validation_errors: ["Invalid JSON"] },
];

describe("APIDeveloperAPIWebhookPayloadInspectorCard", () => {
  it("shows inspections", () => {
    const { container } = render(<APIDeveloperAPIWebhookPayloadInspectorCard inspections={inspections} errorCount={1} appName="App" />);
    expect(container.textContent).toContain("Payload Inspector");
    expect(container.textContent).toContain("1 issues");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("512B");
    expect(container.textContent).toContain("5 fields");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIWebhookPayloadInspectorCard inspections={[]} errorCount={0} appName="App" />);
    expect(container.textContent).toContain("No inspections");
  });
});
