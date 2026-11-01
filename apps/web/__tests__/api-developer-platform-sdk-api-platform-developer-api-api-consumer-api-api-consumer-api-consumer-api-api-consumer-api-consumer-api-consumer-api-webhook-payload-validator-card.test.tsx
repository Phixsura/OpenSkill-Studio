import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-consumer-api-webhook-payload-validator-card";

describe("WebhookPayloadValidatorCard", () => {
  it("shows schemas and validation", () => {
    const schemas = [{ id: "s1", eventType: "order.created", ruleCount: 3 }];
    const lastValidation = { eventType: "order.created", valid: true, errors: [], sizeBytes: 256 };
    const { container } = render(<Card schemas={schemas} lastValidation={lastValidation} appName="App" />);
    expect(container.textContent).toContain("Payload Validator");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("Valid");
    expect(container.textContent).toContain("3 rules");
  });
  it("shows empty", () => {
    const { container } = render(<Card schemas={[]} lastValidation={null} appName="App" />);
    expect(container.textContent).toContain("No schemas registered");
  });
});
