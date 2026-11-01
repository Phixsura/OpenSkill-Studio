import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSkaffoldPanel } from "@/components/fleet-skaffold-panel";
describe("FleetSkaffoldPanel", () => { it("renders", () => {
    const { container } = render(<FleetSkaffoldPanel totalDevs={20} activeLoops={10} avgSync={2500} fast={true} />);
    expect(container.textContent).toContain("Skaffold");
    expect(container.textContent).toContain("Fast inner loop");
}); });
