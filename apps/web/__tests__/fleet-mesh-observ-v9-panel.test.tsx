import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMeshObservV9Panel } from "@/components/fleet-mesh-observ-v9-panel";
describe("FleetMeshObservV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMeshObservV9Panel proxies={50} rps={100000} />);
    expect(container.textContent).toContain("Mesh Observability v9");
}); });
