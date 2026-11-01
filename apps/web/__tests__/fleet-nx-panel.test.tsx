import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNxPanel } from "@/components/fleet-nx-panel";
describe("FleetNxPanel", () => { it("renders", () => {
    const { container } = render(<FleetNxPanel totalProjects={30} affected={10} fromCache={20} avgBuild={15} />);
    expect(container.textContent).toContain("Nx");
    expect(container.textContent).toContain("20 cached");
}); });
