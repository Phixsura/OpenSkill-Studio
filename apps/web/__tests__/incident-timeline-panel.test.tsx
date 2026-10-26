import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentTimelinePanel } from "@/components/incident-timeline-panel";

const mockIncident = {
  id: "inc-1", title: "API Gateway Outage", severity: "sev1" as const,
  status: "identified", assignee: "alice", affectedUsers: 5000,
  rootCause: "Database connection pool exhausted", mttrMinutes: 45,
  timeline: [
    { message: "Incident created", author: "system", status: "open", timestamp: "12:00" },
    { message: "Investigating high error rates", author: "alice", status: "investigating", timestamp: "12:05" },
    { message: "Found DB pool exhaustion", author: "alice", status: "identified", timestamp: "12:15" },
  ],
};

describe("IncidentTimelinePanel", () => {
  it("renders incident details", () => {
    const { container } = render(<IncidentTimelinePanel incident={mockIncident} />);
    expect(container.textContent).toContain("API Gateway Outage");
    expect(container.textContent).toContain("SEV1");
    expect(container.textContent).toContain("identified");
  });

  it("shows affected users and MTTR", () => {
    const { container } = render(<IncidentTimelinePanel incident={mockIncident} />);
    expect(container.textContent).toContain("5,000 affected");
    expect(container.textContent).toContain("45min MTTR");
  });

  it("shows root cause", () => {
    const { container } = render(<IncidentTimelinePanel incident={mockIncident} />);
    expect(container.textContent).toContain("Database connection pool");
  });

  it("renders timeline events", () => {
    const { container } = render(<IncidentTimelinePanel incident={mockIncident} />);
    expect(container.textContent).toContain("Incident created");
    expect(container.textContent).toContain("Investigating high error rates");
    expect(container.textContent).toContain("Found DB pool exhaustion");
  });
});
