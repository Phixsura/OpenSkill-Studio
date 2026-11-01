import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEdgeComputeV9Panel } from "@/components/fleet-edge-compute-v9-panel";
describe("FleetEdgeComputeV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetEdgeComputeV9Panel nodes={200} regions={12} />);
    expect(container.textContent).toContain("Edge Compute v9");
}); });
