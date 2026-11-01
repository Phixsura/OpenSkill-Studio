import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRedwoodPanel } from "@/components/fleet-redwood-panel";
describe("FleetRedwoodPanel", () => { it("renders", () => {
    const { container } = render(<FleetRedwoodPanel apps={3} deployed={3} cells={50} services={30} />);
    expect(container.textContent).toContain("RedwoodJS");
    expect(container.textContent).toContain("50 cells");
}); });
