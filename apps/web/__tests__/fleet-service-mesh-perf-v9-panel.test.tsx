import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceMeshPerfV9Panel } from "@/components/fleet-service-mesh-perf-v9-panel";
describe("FleetServiceMeshPerfV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceMeshPerfV9Panel proxies={100} overhead={1.5} />);
    expect(container.textContent).toContain("Mesh Perf v9");
}); });
