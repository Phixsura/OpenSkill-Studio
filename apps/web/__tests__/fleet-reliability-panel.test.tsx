import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetReliabilityPanel } from "@/components/fleet-reliability-panel";
describe("FleetReliabilityPanel", () => { it("renders", () => {
    const { container } = render(<FleetReliabilityPanel score={95.49} grade="Gold" />);
    expect(container.textContent).toContain("Reliability Score");
    expect(container.textContent).toContain("95.49 — Gold");
}); });
