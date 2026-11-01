import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-payload-encryption-card";

describe("PayloadEncryptionCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", algorithm: "aes-256-gcm", encrypted_fields: ["ssn", "email"] }];
    const { container } = render(<Card configs={configs} totalEncrypted={500} totalFields={1000} appName="App" />);
    expect(container.textContent).toContain("Payload Encryption");
    expect(container.textContent).toContain("aes-256-gcm");
    expect(container.textContent).toContain("ssn");
    expect(container.textContent).toContain("500 payloads");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} totalEncrypted={0} totalFields={0} appName="App" />);
    expect(container.textContent).toContain("No encryption configs");
  });
});
