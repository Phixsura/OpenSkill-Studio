import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGkePanel } from "@/components/fleet-gke-panel";
describe("FleetGkePanel", () => { it("renders", () => {
    const { container } = render(<FleetGkePanel clusters={5} running={5} pods={2000} autopilot={3} />);
    expect(container.textContent).toContain("GKE");
    expect(container.textContent).toContain("3 autopilot");
}); });
