import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SecretsVaultViewer } from "@/components/secrets-vault-viewer";

describe("SecretsVaultViewer", () => {
  it("renders vault", () => {
    const { container } = render(
      <SecretsVaultViewer totalSecrets={3} totalAccesses={50} onRotate={vi.fn()}
        secrets={[
          { name: "DB_PASSWORD", version: 2, accessCount: 30, owner: "platform" },
          { name: "API_KEY", version: 1, accessCount: 20, owner: "api" },
        ]} />
    );
    expect(container.textContent).toContain("Secrets Vault");
    expect(container.textContent).toContain("3 secrets");
    expect(container.textContent).toContain("50 accesses");
    expect(container.textContent).toContain("DB_PASSWORD");
    expect(container.textContent).toContain("v2");
    expect(container.textContent).toContain("Rotate");
  });
});
