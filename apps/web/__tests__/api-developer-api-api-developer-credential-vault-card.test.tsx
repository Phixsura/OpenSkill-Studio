import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperCredentialVaultCard from "../src/components/api-developer-api-api-developer-credential-vault-card";

const entries = [
  { entry_id: "e1", credential_type: "api_key", name: "Prod Key", fingerprint: "abc123def456", access_count: 50, rotated: true },
];

describe("APIDeveloperAPIApiDeveloperCredentialVaultCard", () => {
  it("shows vault entries", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperCredentialVaultCard entries={entries} appName="App" />);
    expect(container.textContent).toContain("Credential Vault");
    expect(container.textContent).toContain("Prod Key");
    expect(container.textContent).toContain("abc123def456");
    expect(container.textContent).toContain("50 uses");
    expect(container.textContent).toContain("rotated");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperCredentialVaultCard entries={[]} appName="App" />);
    expect(container.textContent).toContain("No credentials stored");
  });
});
