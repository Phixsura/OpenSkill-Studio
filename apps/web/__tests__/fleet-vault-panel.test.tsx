import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetVaultPanel } from "@/components/fleet-vault-panel";
describe("FleetVaultPanel", () => { it("renders", () => {
    const { container } = render(<FleetVaultPanel engines={5} sealed={1} totalSecrets={700} healthy={false} />);
    expect(container.textContent).toContain("Vault");
    expect(container.textContent).toContain("1 sealed");
}); });
