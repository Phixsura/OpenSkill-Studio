import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEdgeRoutingV9Panel } from "@/components/fleet-edge-routing-v9-panel";
describe("FleetEdgeRoutingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetEdgeRoutingV9Panel rules={30} rps={500000} />);
    expect(container.textContent).toContain("Edge Routing v9");
}); });
