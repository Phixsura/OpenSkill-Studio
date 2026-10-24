import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPrivVaultPanel } from "@/components/fleet-ai-priv-vault-panel";
describe("FleetAiPrivVaultPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPrivVaultPanel vaults={2} active={2} pii={200000} redacted={200000} tokenized={150000} />);
    expect(container.textContent).toContain("Privacy Vault");
}); });
