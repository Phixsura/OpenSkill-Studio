import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNixPanel } from "@/components/fleet-nix-panel";
describe("FleetNixPanel", () => { it("renders", () => {
    const { container } = render(<FleetNixPanel total={30} usingNix={20} reproducible={15} adoptionPct={66.7} />);
    expect(container.textContent).toContain("Nix");
    expect(container.textContent).toContain("66.7%");
}); });
