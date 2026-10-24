import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNodePoolV9Panel } from "@/components/fleet-node-pool-v9-panel";
describe("FleetNodePoolV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetNodePoolV9Panel pools={5} nodes={100} />);
    expect(container.textContent).toContain("Node Pool v9");
}); });
