import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChaosMeshPanel } from "@/components/fleet-chaos-mesh-panel";
describe("FleetChaosMeshPanel", () => { it("renders", () => {
    const { container } = render(<FleetChaosMeshPanel total={10} running={2} paused={1} completed={7} />);
    expect(container.textContent).toContain("Chaos Mesh");
}); });
