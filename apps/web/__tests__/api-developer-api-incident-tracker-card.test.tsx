import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIIncidentTrackerCard from "../src/components/api-developer-api-incident-tracker-card";

const incidents = [
  { incident_id: "inc-1", title: "API Outage", severity: "critical", status: "open", duration_minutes: 45, affected_endpoints: ["/api/users"] },
  { incident_id: "inc-2", title: "Slow queries", severity: "minor", status: "resolved", duration_minutes: 15, affected_endpoints: [] },
];

describe("APIDeveloperAPIIncidentTrackerCard", () => {
  it("shows incidents", () => {
    const { container } = render(<APIDeveloperAPIIncidentTrackerCard incidents={incidents} mttrMinutes={30} appName="App" />);
    expect(container.textContent).toContain("Incident Tracker");
    expect(container.textContent).toContain("1 open");
    expect(container.textContent).toContain("API Outage");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("MTTR: 30m");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIIncidentTrackerCard incidents={[]} mttrMinutes={0} appName="App" />);
    expect(container.textContent).toContain("No incidents");
  });
});
