import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-webhook-signature-verifier-card";

describe("WebhookSignatureVerifierCard", () => {
  it("shows config and verifications", () => {
    const vf = [{ valid: true, reason: "valid" }, { valid: false, reason: "invalid_signature" }];
    const { container } = render(<Card webhookId="wh1" algorithm="sha256" toleranceSec={300} replayWindow={1000} recentVerifications={vf} appName="App" />);
    expect(container.textContent).toContain("Signature Verifier");
    expect(container.textContent).toContain("SHA256");
    expect(container.textContent).toContain("300s");
    expect(container.textContent).toContain("1 rejected");
  });
  it("shows empty", () => {
    const { container } = render(<Card webhookId="wh1" algorithm="sha256" toleranceSec={300} replayWindow={1000} recentVerifications={[]} appName="App" />);
    expect(container.textContent).toContain("No verifications yet");
  });
});
