import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import IncidentTrackerCard from "../src/components/incident-tracker-card";

const activeIncident = {
  incident_id: "inc-1",
  title: "API Response Degradation",
  severity: "critical" as const,
  status: "identified" as const,
  affected_components: ["api", "auth"],
  timeline: [
    {
      status: "investigating",
      message: "Investigating slow responses",
      timestamp: new Date().toISOString(),
    },
    {
      status: "identified",
      message: "DB connection pool exhausted",
      timestamp: new Date().toISOString(),
    },
  ],
  created_at: new Date(Date.now() - 1_800_000).toISOString(),
  duration_minutes: 30,
};

const resolvedIncident = {
  incident_id: "inc-2",
  title: "Login Service Outage",
  severity: "major" as const,
  status: "resolved" as const,
  affected_components: ["auth"],
  timeline: [
    {
      status: "investigating",
      message: "Users unable to log in",
      timestamp: new Date().toISOString(),
    },
    { status: "resolved", message: "Deployed hotfix", timestamp: new Date().toISOString() },
  ],
  created_at: new Date(Date.now() - 7_200_000).toISOString(),
  duration_minutes: 90,
};

const minorIncident = {
  incident_id: "inc-3",
  title: "Webhook Delays",
  severity: "minor" as const,
  status: "monitoring" as const,
  affected_components: [],
  timeline: [
    {
      status: "monitoring",
      message: "Watching webhook queue",
      timestamp: new Date().toISOString(),
    },
  ],
  created_at: new Date(Date.now() - 600_000).toISOString(),
  duration_minutes: 10,
};

describe("IncidentTrackerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <IncidentTrackerCard incidents={[activeIncident]} appName="My App" />,
    );
    expect(container.textContent).toContain("Incidents");
    expect(container.textContent).toContain("My App");
  });

  it("shows active count", () => {
    const { container } = render(
      <IncidentTrackerCard incidents={[activeIncident, minorIncident]} appName="App" />,
    );
    expect(container.textContent).toContain("2 active");
  });

  it("shows all-clear when no active incidents", () => {
    const { container } = render(
      <IncidentTrackerCard incidents={[resolvedIncident]} appName="App" />,
    );
    expect(container.textContent).toContain("All clear");
  });

  it("renders incident title and severity", () => {
    const { container } = render(
      <IncidentTrackerCard incidents={[activeIncident]} appName="App" />,
    );
    expect(container.textContent).toContain("API Response Degradation");
    expect(container.textContent).toContain("critical");
  });

  it("shows status icon", () => {
    const { container } = render(
      <IncidentTrackerCard incidents={[activeIncident]} appName="App" />,
    );
    expect(container.textContent).toContain("🎯");
  });

  it("shows duration", () => {
    const { container } = render(
      <IncidentTrackerCard incidents={[resolvedIncident]} appName="App" />,
    );
    expect(container.textContent).toContain("1h 30m");
  });

  it("renders affected components", () => {
    const { container } = render(
      <IncidentTrackerCard incidents={[activeIncident]} appName="App" />,
    );
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("auth");
  });

  it("shows latest timeline message", () => {
    const { container } = render(
      <IncidentTrackerCard incidents={[activeIncident]} appName="App" />,
    );
    expect(container.textContent).toContain("DB connection pool exhausted");
  });

  it("shows empty state", () => {
    const { container } = render(<IncidentTrackerCard incidents={[]} appName="App" />);
    expect(container.textContent).toContain("No incidents");
  });
});
