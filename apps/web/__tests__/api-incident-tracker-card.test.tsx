import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIIncidentTrackerCard from "../src/components/api-incident-tracker-card";

const incidents = [
  { incident_id: "inc-1", title: "API Down", severity: "critical" as const, status: "investigating" as const, affected_endpoints: ["/api"] },
  { incident_id: "inc-2", title: "Slow Queries", severity: "medium" as const, status: "resolved" as const, affected_endpoints: [] },
];

describe("APIIncidentTrackerCard", () => {
  it("renders header and active count", () => {
    const { container } = render(<APIIncidentTrackerCard incidents={incidents} appName="App" />);
    expect(container.textContent).toContain("Incident Tracker");
    expect(container.textContent).toContain("1 active");
  });

  it("shows severity and status", () => {
    const { container } = render(<APIIncidentTrackerCard incidents={incidents} appName="App" />);
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("API Down");
    expect(container.textContent).toContain("investigating");
  });

  it("shows clean state", () => {
    const { container } = render(<APIIncidentTrackerCard incidents={[]} appName="App" />);
    expect(container.textContent).toContain("No incidents");
  });
});
