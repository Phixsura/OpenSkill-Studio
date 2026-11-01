import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMeshTelemPanel } from "@/components/fleet-mesh-telem-panel";
describe("FleetMeshTelemPanel", () => { it("renders", () => {
    const { container } = render(<FleetMeshTelemPanel proxies={10} totalRps={3000} avgLatency={8} errors={3} healthy={false} />);
    expect(container.textContent).toContain("Mesh Telemetry");
    expect(container.textContent).toContain("3 proxy errors");
}); });
