import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDepDepthPanel } from "@/components/fleet-dep-depth-panel";
describe("FleetDepDepthPanel", () => { it("renders", () => {
    const { container } = render(<FleetDepDepthPanel services={30} maxDepth={7} avgDepth={3} tooDeep={2} manageable={false} />);
    expect(container.textContent).toContain("Dep Tree Depth");
    expect(container.textContent).toContain("2 too deep");
}); });
