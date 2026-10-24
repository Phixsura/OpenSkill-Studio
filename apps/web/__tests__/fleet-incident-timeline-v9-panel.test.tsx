import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIncidentTimelineV9Panel } from "@/components/fleet-incident-timeline-v9-panel";
describe("FleetIncidentTimelineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetIncidentTimelineV9Panel incidents={10} resolved={10} />);
    expect(container.textContent).toContain("Incident Timeline v9");
}); });
