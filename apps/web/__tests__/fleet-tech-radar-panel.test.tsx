import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTechRadarPanel } from "@/components/fleet-tech-radar-panel";
describe("FleetTechRadarPanel", () => { it("renders", () => {
    const { container } = render(<FleetTechRadarPanel total={20} adopt={8} trial={5} assess={4} hold={3} />);
    expect(container.textContent).toContain("Tech Radar");
    expect(container.textContent).toContain("8 adopt");
}); });
