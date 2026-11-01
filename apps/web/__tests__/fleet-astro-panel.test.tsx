import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAstroPanel } from "@/components/fleet-astro-panel";
describe("FleetAstroPanel", () => { it("renders", () => {
    const { container } = render(<FleetAstroPanel sites={10} deployed={10} pages={1000} islands={100} />);
    expect(container.textContent).toContain("Astro");
    expect(container.textContent).toContain("100 islands");
}); });
