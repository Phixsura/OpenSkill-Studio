import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CredentialVaultCard from "../src/components/credential-vault-card";

const credentials = [
  {
    credential_id: "db-pw",
    name: "Database Password",
    prefix: "supe",
    version: 3,
    rotated_at: new Date(Date.now() - 86400000).toISOString(),
  },
  { credential_id: "api-key", name: "API Key", prefix: "sk_l", version: 1, rotated_at: null },
];

describe("CredentialVaultCard", () => {
  it("renders header", () => {
    const { container } = render(
      <CredentialVaultCard credentials={credentials} appName="My App" />,
    );
    expect(container.textContent).toContain("Credential Vault");
  });

  it("shows stored count", () => {
    const { container } = render(<CredentialVaultCard credentials={credentials} appName="App" />);
    expect(container.textContent).toContain("2 stored");
  });

  it("renders names and prefixes", () => {
    const { container } = render(<CredentialVaultCard credentials={credentials} appName="App" />);
    expect(container.textContent).toContain("Database Password");
    expect(container.textContent).toContain("supe");
    expect(container.textContent).toContain("sk_l");
  });

  it("shows versions", () => {
    const { container } = render(<CredentialVaultCard credentials={credentials} appName="App" />);
    expect(container.textContent).toContain("v3");
  });

  it("shows rotation time", () => {
    const { container } = render(<CredentialVaultCard credentials={credentials} appName="App" />);
    expect(container.textContent).toContain("rotated");
    expect(container.textContent).toContain("never");
  });

  it("shows empty state", () => {
    const { container } = render(<CredentialVaultCard credentials={[]} appName="App" />);
    expect(container.textContent).toContain("No credentials stored");
  });
});
