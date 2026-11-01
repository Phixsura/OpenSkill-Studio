import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookPayloadEncryptionCard from "../src/components/api-developer-api-api-webhook-payload-encryption-card";

const configs = [{ destination: "https://api.example.com", algorithm: "aes-256-gcm", key_fingerprint: "abc123", enabled: true, payloads_encrypted: 5000 }];

describe("APIDeveloperAPIApiWebhookPayloadEncryptionCard", () => {
  it("shows encryption configs", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookPayloadEncryptionCard configs={configs} stats={{ destinations: 1, payloads_encrypted: 5000, bytes_encrypted: 2097152 }} appName="App" />);
    expect(container.textContent).toContain("Payload Encryption");
    expect(container.textContent).toContain("2.0MB encrypted");
    expect(container.textContent).toContain("aes-256-gcm");
    expect(container.textContent).toContain("5000 enc");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookPayloadEncryptionCard configs={[]} stats={{ destinations: 0, payloads_encrypted: 0, bytes_encrypted: 0 }} appName="App" />);
    expect(container.textContent).toContain("No encryption configs");
  });
});
