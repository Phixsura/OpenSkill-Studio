import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTokenVaultV9Panel } from "@/components/fleet-token-vault-v9-panel";
describe("FleetTokenVaultV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTokenVaultV9Panel tokens={1000} calls={500000} />);
    expect(container.textContent).toContain("Token Vault v9");
}); });
