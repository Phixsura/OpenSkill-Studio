import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentTimelineView } from "@/components/incident-timeline-view";

describe("IncidentTimelineView", () => {
  it("renders events", () => {
    const events = [
      { time: "2026-01-01T10:00:00Z", type: "opened", message: "API down" },
      { time: "2026-01-01T10:10:00Z", type: "update", message: "Investigating", author: "alice" },
      { time: "2026-01-01T10:30:00Z", type: "resolved", message: "Fixed" },
    ];
    const { container } = render(<IncidentTimelineView incidentId="inc1" events={events} durationMinutes={30} />);
    expect(container.textContent).toContain("API down");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("30 min");
  });
  it("shows ongoing", () => {
    const { container } = render(<IncidentTimelineView incidentId="inc2" events={[]} durationMinutes={null} />);
    expect(container.textContent).toContain("Ongoing");
  });
});
