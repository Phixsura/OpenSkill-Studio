import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentTimelinePanel } from "@/components/incident-timeline-panel";

describe("IncidentTimelinePanel", () => {
  it("shows all operational when empty", () => {
    const { container } = render(<IncidentTimelinePanel incidents={[]} />);
    expect(container.textContent).toContain("All Systems Operational");
  });
  it("renders incidents", () => {
    const incidents = [{
      incidentId: "inc-1", title: "API Latency", severity: "major", resolved: false,
      events: [{ eventId: "e1", status: "investigating", message: "Looking into it", timestamp: Date.now() }],
    }];
    const { container } = render(<IncidentTimelinePanel incidents={incidents} />);
    expect(container.textContent).toContain("API Latency");
    expect(container.textContent).toContain("investigating");
  });
});
