import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-webhook-secret-manager-card";

describe("WebhookSecretManagerCard", () => {
  it("shows secrets", () => {
    const secrets = [{ consumer_id: "c1", masked_value: "whsec_***ab12", version: 2, rotated: false }];
    const { container } = render(<Card secrets={secrets} appName="App" />);
    expect(container.textContent).toContain("Webhook Secrets");
    expect(container.textContent).toContain("whsec_***ab12");
    expect(container.textContent).toContain("v2");
  });
  it("shows empty", () => {
    const { container } = render(<Card secrets={[]} appName="App" />);
    expect(container.textContent).toContain("No webhook secrets");
  });
});
