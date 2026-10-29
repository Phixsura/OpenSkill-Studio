import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-credential-vault-card";

describe("CredentialVaultCard", () => {
  it("shows credentials", () => {
    const entries = [{ entry_id: "k1", credential_type: "api_key", masked_value: "***1234", rotated: false }];
    const { container } = render(<Card consumerId="c1" entries={entries} appName="App" />);
    expect(container.textContent).toContain("Credential Vault");
    expect(container.textContent).toContain("api_key");
    expect(container.textContent).toContain("***1234");
  });
  it("shows empty", () => {
    const { container } = render(<Card consumerId="c1" entries={[]} appName="App" />);
    expect(container.textContent).toContain("No credentials stored");
  });
});
