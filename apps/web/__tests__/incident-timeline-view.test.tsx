import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentTimelineView } from "@/components/incident-timeline-view";

describe("IncidentTimelineView", () => {
  it("renders incident", () => {
    const { container } = render(
      <IncidentTimelineView incidentId="INC-0001" title="DB Outage"
        severity="sev1" status="resolved" commander="alice" affected={["database", "api"]}
        events={[
          { action: "declared", by: "alice" },
          { action: "identified", note: "Disk full", by: "alice" },
          { action: "resolved", note: "Expanded disk", by: "alice" },
        ]} />
    );
    expect(container.textContent).toContain("INC-0001");
    expect(container.textContent).toContain("DB Outage");
    expect(container.textContent).toContain("sev1");
    expect(container.textContent).toContain("resolved");
    expect(container.textContent).toContain("declared");
    expect(container.textContent).toContain("Disk full");
    expect(container.textContent).toContain("Commander: alice");
  });
});
