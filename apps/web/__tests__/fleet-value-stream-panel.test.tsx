import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetValueStreamPanel } from "@/components/fleet-value-stream-panel";
describe("FleetValueStreamPanel", () => { it("renders", () => {
    const { container } = render(<FleetValueStreamPanel stages={5} totalCycle={60} efficiencyPct={58} bottleneck="review" />);
    expect(container.textContent).toContain("Value Stream");
    expect(container.textContent).toContain("review");
}); });
