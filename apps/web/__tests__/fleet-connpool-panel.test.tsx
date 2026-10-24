import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConnpoolPanel } from "@/components/fleet-connpool-panel";
describe("FleetConnpoolPanel", () => { it("renders", () => {
    const { container } = render(<FleetConnpoolPanel used={85} max={100} pct={85} saturated={false} />);
    expect(container.textContent).toContain("Fleet Connections");
    expect(container.textContent).toContain("85/100");
}); });
