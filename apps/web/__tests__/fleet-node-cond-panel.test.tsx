import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNodeCondPanel } from "@/components/fleet-node-cond-panel";
describe("FleetNodeCondPanel", () => { it("renders", () => {
    const { container } = render(<FleetNodeCondPanel total={5} notReady={1} pressure={1} allHealthy={false} />);
    expect(container.textContent).toContain("Node Conditions");
    expect(container.textContent).toContain("1 not ready");
}); });
