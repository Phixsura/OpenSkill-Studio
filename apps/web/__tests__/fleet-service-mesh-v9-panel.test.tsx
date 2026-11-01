import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceMeshV9Panel } from "@/components/fleet-service-mesh-v9-panel";
describe("FleetServiceMeshV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceMeshV9Panel services={200} rps={80000} />);
    expect(container.textContent).toContain("Service Mesh v9");
}); });
