import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-webhook-payload-encryption-card";

describe("WebhookPayloadEncryptionCard", () => {
  it("shows configs", () => {
    const configs = [{ webhookId: "w1", algorithm: "aes-256-gcm", keyVersion: 2, enabled: true }];
    const { container } = render(<Card configs={configs} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Payload Encryption");
    expect(container.textContent).toContain("w1");
    expect(container.textContent).toContain("aes-256-gcm");
    expect(container.textContent).toContain("v2");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No encryption configured");
  });
});
