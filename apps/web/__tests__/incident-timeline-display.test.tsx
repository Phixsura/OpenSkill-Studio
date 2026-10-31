import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentTimelineDisplay } from "@/components/incident-timeline-display";

describe("IncidentTimelineDisplay", () => {
  const incidents = [
    { id: "i1", title: "API spike", severity: "minor", started: "2026-10-18T00:00:00", resolved: "2026-10-18T02:00:00", duration_min: 120, affected: ["API"] },
    { id: "i2", title: "CDN down", severity: "critical", started: "2026-08-24T00:00:00", resolved: "2026-08-24T01:00:00", duration_min: 60, affected: ["CDN"] },
  ];
  it("renders", () => {
    const { container } = render(
      <IncidentTimelineDisplay incidents={incidents} uptimePct={99.86} mttrMin={90} />
    );
    expect(container.textContent).toContain("Incident History");
    expect(container.textContent).toContain("99.86%");
    expect(container.textContent).toContain("API spike");
    expect(container.textContent).toContain("critical");
  });
});
