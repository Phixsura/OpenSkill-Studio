import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetZookeeperPanel } from "@/components/fleet-zookeeper-panel";
describe("FleetZookeeperPanel", () => { it("renders", () => {
    const { container } = render(<FleetZookeeperPanel nodes={3} leader={1} followers={2} avgLatency={3} quorum={true} />);
    expect(container.textContent).toContain("Zookeeper");
    expect(container.textContent).toContain("1L/2F");
}); });
