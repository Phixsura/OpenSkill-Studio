import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecretsVaultPanel } from "@/components/secrets-vault-panel";

describe("SecretsVaultPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SecretsVaultPanel totalAccesses={150}
        secrets={[
          { key: "db_password", fingerprint: "abc123def456", version: 3, owner: "admin" },
          { key: "api_key", fingerprint: "xyz789abc012", version: 1, owner: "ci" },
        ]} />
    );
    expect(container.textContent).toContain("Secrets Vault");
    expect(container.textContent).toContain("2 secrets");
    expect(container.textContent).toContain("150 accesses");
    expect(container.textContent).toContain("db_password");
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("abc123def456");
  });
});
