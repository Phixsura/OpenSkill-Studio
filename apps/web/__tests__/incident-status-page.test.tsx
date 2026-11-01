import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentStatusPage } from "@/components/incident-status-page";

const MOCK_INCIDENTS = [
  {
    incident_id: "inc-1",
    title: "API Gateway Timeout",
    severity: "critical" as const,
    status: "investigating" as const,
    affected_components: ["api", "gateway"],
    timeline: [
      {
        status: "investigating",
        message: "Elevated error rates detected",
        timestamp: "2026-10-28T14:00:00Z",
        author: "monitor",
      },
    ],
    created_at: "2026-10-28T14:00:00Z",
    duration_minutes: null,
  },
  {
    incident_id: "inc-2",
    title: "Webhook Delivery Delay",
    severity: "minor" as const,
    status: "resolved" as const,
    affected_components: ["webhooks"],
    timeline: [
      {
        status: "investigating",
        message: "Delays reported",
        timestamp: "2026-10-27T10:00:00Z",
        author: "eng",
      },
      {
        status: "resolved",
        message: "Queue flushed",
        timestamp: "2026-10-27T10:30:00Z",
        author: "eng",
      },
    ],
    created_at: "2026-10-27T10:00:00Z",
    duration_minutes: 30,
  },
];

const MOCK_SUMMARY = { total: 5, open: 1, resolved: 4, mttr_minutes: 25.3 };
const CLEAR_SUMMARY = { total: 3, open: 0, resolved: 3, mttr_minutes: 15.0 };

describe("IncidentStatusPage", () => {
  it("renders heading and app name", () => {
    const { container } = render(
      <IncidentStatusPage appName="My App" incidents={MOCK_INCIDENTS} summary={MOCK_SUMMARY} />,
    );
    expect(container.textContent).toContain("Incident Status");
    expect(container.textContent).toContain("My App");
  });

  it("shows active incidents banner", () => {
    const { container } = render(
      <IncidentStatusPage appName="App" incidents={MOCK_INCIDENTS} summary={MOCK_SUMMARY} />,
    );
    expect(container.textContent).toContain("1 Active Incident");
  });

  it("shows all clear banner", () => {
    const { container } = render(
      <IncidentStatusPage appName="App" incidents={MOCK_INCIDENTS} summary={CLEAR_SUMMARY} />,
    );
    expect(container.textContent).toContain("All Systems Operational");
  });

  it("renders summary stats", () => {
    const { container } = render(
      <IncidentStatusPage appName="App" incidents={MOCK_INCIDENTS} summary={MOCK_SUMMARY} />,
    );
    expect(container.textContent).toContain("5"); // total
    expect(container.textContent).toContain("4"); // resolved
    expect(container.textContent).toContain("25.3m"); // MTTR
  });

  it("renders MTTR dash when null", () => {
    const noMttr = { ...MOCK_SUMMARY, mttr_minutes: null };
    const { container } = render(
      <IncidentStatusPage appName="App" incidents={[]} summary={noMttr} />,
    );
    expect(container.textContent).toContain("—");
  });

  it("renders incident titles", () => {
    const { container } = render(
      <IncidentStatusPage appName="App" incidents={MOCK_INCIDENTS} summary={MOCK_SUMMARY} />,
    );
    expect(container.textContent).toContain("API Gateway Timeout");
    expect(container.textContent).toContain("Webhook Delivery Delay");
  });

  it("renders status badges", () => {
    const { container } = render(
      <IncidentStatusPage appName="App" incidents={MOCK_INCIDENTS} summary={MOCK_SUMMARY} />,
    );
    expect(container.textContent).toContain("Investigating");
    expect(container.textContent).toContain("Resolved");
  });

  it("renders affected components", () => {
    const { container } = render(
      <IncidentStatusPage appName="App" incidents={MOCK_INCIDENTS} summary={MOCK_SUMMARY} />,
    );
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("gateway");
    expect(container.textContent).toContain("webhooks");
  });

  it("renders timeline messages", () => {
    const { container } = render(
      <IncidentStatusPage appName="App" incidents={MOCK_INCIDENTS} summary={MOCK_SUMMARY} />,
    );
    expect(container.textContent).toContain("Elevated error rates");
    expect(container.textContent).toContain("Queue flushed");
  });

  it("renders duration", () => {
    const { container } = render(
      <IncidentStatusPage appName="App" incidents={MOCK_INCIDENTS} summary={MOCK_SUMMARY} />,
    );
    expect(container.textContent).toContain("30m");
  });

  it("shows empty state", () => {
    const { container } = render(
      <IncidentStatusPage appName="App" incidents={[]} summary={CLEAR_SUMMARY} />,
    );
    expect(container.textContent).toContain("No incidents recorded");
  });

  it("renders severity dots", () => {
    const { container } = render(
      <IncidentStatusPage appName="App" incidents={MOCK_INCIDENTS} summary={MOCK_SUMMARY} />,
    );
    // Critical and minor severity dots should be present
    expect(container.querySelector(".bg-red-500")).toBeTruthy();
    expect(container.querySelector(".bg-yellow-500")).toBeTruthy();
  });
});
