import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-incident-timeline-card";

describe("IncidentTimelineCard", () => {
  it("shows incidents", () => {
    const incidents = [{ incident_id: "inc-1", title: "DB outage", severity: "critical", current_phase: "investigating", timeline: [], duration_minutes: 0 }];
    const { container } = render(<Card incidents={incidents} activeCount={1} appName="App" />);
    expect(container.textContent).toContain("Incidents");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("DB outage");
    expect(container.textContent).toContain("investigating");
  });
  it("shows empty", () => {
    const { container } = render(<Card incidents={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No incidents");
  });
});
