import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGrandTotalPanel } from "@/components/fleet-grand-total-panel";
describe("FleetGrandTotalPanel", () => { it("renders", () => {
    const { container } = render(<FleetGrandTotalPanel />);
    expect(container.textContent).toContain("OpenSkill Developer Platform");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
}); });
