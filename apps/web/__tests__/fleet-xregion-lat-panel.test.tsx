import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetXregionLatPanel } from "@/components/fleet-xregion-lat-panel";
describe("FleetXregionLatPanel", () => { it("renders", () => {
    const { container } = render(<FleetXregionLatPanel pairs={6} avgLatency={175} highLatency={1} acceptable={false} />);
    expect(container.textContent).toContain("Cross-Region Latency");
    expect(container.textContent).toContain("1 high-latency");
}); });
