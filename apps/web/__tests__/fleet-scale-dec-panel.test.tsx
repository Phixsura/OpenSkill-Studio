import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetScaleDecPanel } from "@/components/fleet-scale-dec-panel";
describe("FleetScaleDecPanel", () => { it("renders", () => {
    const { container } = render(<FleetScaleDecPanel cpuPct={85} memPct={60} queueDepth={500} action="scale_up" />);
    expect(container.textContent).toContain("Scaling Decision");
    expect(container.textContent).toContain("SCALE UP");
}); });
