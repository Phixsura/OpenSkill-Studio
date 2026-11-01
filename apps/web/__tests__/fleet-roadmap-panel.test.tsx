import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRoadmapPanel } from "@/components/fleet-roadmap-panel";
describe("FleetRoadmapPanel", () => { it("renders", () => {
    const { container } = render(<FleetRoadmapPanel total={20} done={12} inProgress={5} planned={3} completionPct={60} />);
    expect(container.textContent).toContain("Roadmap");
    expect(container.textContent).toContain("60% done");
}); });
