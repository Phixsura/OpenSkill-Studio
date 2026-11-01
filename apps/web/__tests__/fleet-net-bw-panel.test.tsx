import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNetBwPanel } from "@/components/fleet-net-bw-panel";
describe("FleetNetBwPanel", () => { it("renders", () => {
    const { container } = render(<FleetNetBwPanel totalGbps={20} usedGbps={17} utilPct={85} saturated={true} />);
    expect(container.textContent).toContain("Network Bandwidth");
    expect(container.textContent).toContain("Near saturation");
}); });
