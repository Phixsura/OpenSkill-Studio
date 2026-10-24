import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMeshTrafficV9Panel } from "@/components/fleet-mesh-traffic-v9-panel";
describe("FleetMeshTrafficV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMeshTrafficV9Panel splits={20} rps={100000} />);
    expect(container.textContent).toContain("Mesh Traffic v9");
}); });
