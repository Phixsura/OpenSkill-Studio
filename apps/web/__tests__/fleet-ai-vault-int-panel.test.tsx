import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiVaultIntPanel } from "@/components/fleet-ai-vault-int-panel";
describe("FleetAiVaultIntPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiVaultIntPanel vaults={3} active={3} secrets={5000} accesses={20000000} rotations={300} />);
    expect(container.textContent).toContain("AI Vault");
}); });
