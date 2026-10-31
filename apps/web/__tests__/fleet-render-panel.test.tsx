import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRenderPanel } from "@/components/fleet-render-panel";
describe("FleetRenderPanel", () => { it("renders", () => {
    const { container } = render(<FleetRenderPanel services={20} running={18} suspended={2} />);
    expect(container.textContent).toContain("Render");
    expect(container.textContent).toContain("2 suspended");
}); });
