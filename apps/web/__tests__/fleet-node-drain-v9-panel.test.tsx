import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNodeDrainV9Panel } from "@/components/fleet-node-drain-v9-panel";
describe("FleetNodeDrainV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetNodeDrainV9Panel nodes={50} draining={0} />);
    expect(container.textContent).toContain("Node Drain v9");
}); });
