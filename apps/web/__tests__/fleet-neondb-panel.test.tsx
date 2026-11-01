import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNeondbPanel } from "@/components/fleet-neondb-panel";
describe("FleetNeondbPanel", () => { it("renders", () => {
    const { container } = render(<FleetNeondbPanel projects={8} active={8} computeHours={50} branches={20} />);
    expect(container.textContent).toContain("Neon");
    expect(container.textContent).toContain("20 branches");
}); });
