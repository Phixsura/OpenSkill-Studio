import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IncidentResponseTimeline } from "@/components/incident-response-timeline";

describe("IncidentResponseTimeline", () => {
  const timeline = [
    { action: "created", by: "alice", at: "2026-10-23T12:00:00" },
    { action: "identified", message: "Root cause found", by: "bob", at: "2026-10-23T12:30:00" },
  ];
  it("renders", () => {
    const { container } = render(
      <IncidentResponseTimeline incidentId="INC-ABC1" title="API Down" severity="sev1"
        severityLabel="Critical" status="identified" affectedServices={["api"]}
        timeline={timeline} onUpdate={vi.fn()} />
    );
    expect(container.textContent).toContain("INC-ABC1");
    expect(container.textContent).toContain("API Down");
    expect(container.textContent).toContain("Critical");
    expect(container.textContent).toContain("created");
    expect(container.textContent).toContain("Root cause found");
    expect(container.textContent).toContain("Post Update");
  });
});
