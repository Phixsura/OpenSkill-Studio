import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-webhook-payload-transform-card";

describe("WebhookPayloadTransformCard", () => {
  it("shows rules", () => {
    const rules = [{ rule_id: "r1", source: "data.email", target: "contact.email" }];
    const { container } = render(<Card configId="c1" webhookId="wh1" rules={rules} dropUnmapped={false} appName="App" />);
    expect(container.textContent).toContain("Payload Transform");
    expect(container.textContent).toContain("data.email");
    expect(container.textContent).toContain("contact.email");
    expect(container.textContent).toContain("Passthrough");
  });
  it("shows strict mode", () => {
    const { container } = render(<Card configId="c1" webhookId="wh1" rules={[]} dropUnmapped={true} appName="App" />);
    expect(container.textContent).toContain("Strict (drop unmapped)");
    expect(container.textContent).toContain("No transform rules");
  });
});
