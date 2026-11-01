import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBoundaryPanel } from "@/components/fleet-boundary-panel";
describe("FleetBoundaryPanel", () => { it("renders", () => {
    const { container } = render(<FleetBoundaryPanel targets={20} activeSessions={15} authorized={20} />);
    expect(container.textContent).toContain("Boundary");
    expect(container.textContent).toContain("15 sessions");
}); });
