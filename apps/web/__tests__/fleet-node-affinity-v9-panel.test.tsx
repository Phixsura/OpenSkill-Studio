import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNodeAffinityV9Panel } from "@/components/fleet-node-affinity-v9-panel";
describe("FleetNodeAffinityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetNodeAffinityV9Panel rules={30} violations={0} />);
    expect(container.textContent).toContain("Node Affinity v9");
}); });
