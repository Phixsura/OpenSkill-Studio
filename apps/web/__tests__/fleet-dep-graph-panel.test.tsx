import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDepGraphPanel } from "@/components/fleet-dep-graph-panel";
describe("FleetDepGraphPanel", () => { it("renders", () => {
    const { container } = render(<FleetDepGraphPanel nodes={10} edges={15} roots={2} leaves={4} />);
    expect(container.textContent).toContain("Dependency Graph");
    expect(container.textContent).toContain("10 nodes");
}); });
