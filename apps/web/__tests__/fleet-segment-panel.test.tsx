import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSegmentPanel } from "@/components/fleet-segment-panel";
describe("FleetSegmentPanel", () => { it("renders", () => {
    const { container } = render(<FleetSegmentPanel workspaces={3} active={3} events={30000000} sources={50} destinations={40} />);
    expect(container.textContent).toContain("Segment");
}); });
