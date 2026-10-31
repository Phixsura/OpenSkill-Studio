import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppHealthDashboard } from "@/components/app-health-dashboard";

const HEALTHY_DATA = {
  installation_id: "inst-1",
  app_name: "My Analytics App",
  current_status: "healthy" as const,
  last_heartbeat_at: "2026-10-28T14:00:00Z",
  consecutive_failures: 0,
  uptime_24h: {
    window_hours: 24,
    total_checks: 1440,
    successful_checks: 1440,
    uptime_pct: 100.0,
    downtime_minutes: 0,
  },
  uptime_7d: {
    window_hours: 168,
    total_checks: 10080,
    successful_checks: 10070,
    uptime_pct: 99.901,
    downtime_minutes: 1.7,
  },
  uptime_30d: {
    window_hours: 720,
    total_checks: 43200,
    successful_checks: 43100,
    uptime_pct: 99.768,
    downtime_minutes: 100.8,
  },
  sla_compliance: {
    target_pct: 99.5,
    actual_pct: 99.768,
    compliant: true,
    budget_remaining_minutes: 115.8,
  },
  recent_events: [
    { status: "healthy" as const, timestamp: "2026-10-28T14:00:00Z", reason: "Heartbeat received" },
    { status: "degraded" as const, timestamp: "2026-10-28T13:55:00Z", reason: "Probe timeout" },
  ],
};

const DOWN_DATA = {
  ...HEALTHY_DATA,
  app_name: "Broken App",
  current_status: "down" as const,
  consecutive_failures: 7,
  sla_compliance: {
    target_pct: 99.5,
    actual_pct: 95.0,
    compliant: false,
    budget_remaining_minutes: 0,
  },
};

describe("AppHealthDashboard", () => {
  it("renders app name", () => {
    const { container } = render(<AppHealthDashboard health={HEALTHY_DATA} />);
    expect(container.textContent).toContain("My Analytics App");
  });

  it("renders healthy status", () => {
    const { container } = render(<AppHealthDashboard health={HEALTHY_DATA} />);
    expect(container.textContent).toContain("Healthy");
  });

  it("renders down status", () => {
    const { container } = render(<AppHealthDashboard health={DOWN_DATA} />);
    expect(container.textContent).toContain("Down");
  });

  it("shows last heartbeat time", () => {
    const { container } = render(<AppHealthDashboard health={HEALTHY_DATA} />);
    expect(container.textContent).toContain("Last heartbeat:");
    expect(container.textContent).not.toContain("Never");
  });

  it("shows Never when no heartbeat", () => {
    const noHb = { ...HEALTHY_DATA, last_heartbeat_at: null };
    const { container } = render(<AppHealthDashboard health={noHb} />);
    expect(container.textContent).toContain("Never");
  });

  it("renders uptime cards for all windows", () => {
    const { container } = render(<AppHealthDashboard health={HEALTHY_DATA} />);
    expect(container.textContent).toContain("24 Hours");
    expect(container.textContent).toContain("7 Days");
    expect(container.textContent).toContain("30 Days");
    expect(container.textContent).toContain("100.00%");
    expect(container.textContent).toContain("99.90%");
  });

  it("renders SLA compliant badge", () => {
    const { container } = render(<AppHealthDashboard health={HEALTHY_DATA} />);
    expect(container.textContent).toContain("Compliant");
    expect(container.textContent).toContain("99.5%");
  });

  it("renders SLA breached badge", () => {
    const { container } = render(<AppHealthDashboard health={DOWN_DATA} />);
    expect(container.textContent).toContain("Breached");
  });

  it("shows consecutive failures warning", () => {
    const { container } = render(<AppHealthDashboard health={DOWN_DATA} />);
    expect(container.textContent).toContain("7 consecutive probe failures");
  });

  it("hides failures warning when zero", () => {
    const { container } = render(<AppHealthDashboard health={HEALTHY_DATA} />);
    expect(container.textContent).not.toContain("consecutive probe");
  });

  it("renders recent events timeline", () => {
    const { container } = render(<AppHealthDashboard health={HEALTHY_DATA} />);
    expect(container.textContent).toContain("Recent Events");
    expect(container.textContent).toContain("Heartbeat received");
    expect(container.textContent).toContain("Probe timeout");
  });

  it("handles singular failure count", () => {
    const one = { ...DOWN_DATA, consecutive_failures: 1 };
    const { container } = render(<AppHealthDashboard health={one} />);
    expect(container.textContent).toContain("1 consecutive probe failure");
    expect(container.textContent).not.toContain("failures");
  });

  it("shows downtime in uptime cards", () => {
    const { container } = render(<AppHealthDashboard health={HEALTHY_DATA} />);
    expect(container.textContent).toContain("No downtime");
    expect(container.textContent).toContain("2min downtime"); // 7d window
  });

  it("renders budget remaining", () => {
    const { container } = render(<AppHealthDashboard health={HEALTHY_DATA} />);
    expect(container.textContent).toContain("116min remaining");
  });
});
