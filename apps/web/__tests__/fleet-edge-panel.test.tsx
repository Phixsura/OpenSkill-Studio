import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEdgePanel } from "@/components/fleet-edge-panel";
describe("FleetEdgePanel", () => { it("renders", () => {
    const { container } = render(<FleetEdgePanel total={20} online={18} offline={2} totalRps={50000} allOnline={false} />);
    expect(container.textContent).toContain("Edge Computing");
    expect(container.textContent).toContain("2 nodes offline");
}); });
