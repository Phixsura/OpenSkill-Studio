import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMeshObsPanel } from "@/components/fleet-mesh-obs-panel";
describe("FleetMeshObsPanel", () => { it("renders", () => {
    const { container } = render(<FleetMeshObsPanel total={20} fullObs={16} coveragePct={80} />);
    expect(container.textContent).toContain("Mesh Observability");
    expect(container.textContent).toContain("80%");
}); });
