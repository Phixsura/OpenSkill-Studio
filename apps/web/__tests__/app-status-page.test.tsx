import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppStatusPage } from "@/components/app-status-page";

const FULL_PAGE = {
  app_name: "My App",
  system_status: "minor_issues" as const,
  components: [
    { name: "API Gateway", status: "operational" as const, uptime_pct: 99.99 },
    { name: "Webhooks", status: "degraded" as const, uptime_pct: 98.5 },
    { name: "Database", status: "maintenance" as const, uptime_pct: 99.9 },
  ],
  active_incidents: [
    {
      title: "Webhook delays",
      status: "investigating",
      severity: "minor",
      last_update: "Looking into delivery delays",
    },
  ],
  maintenance_windows: [
    {
      title: "DB Migration",
      scheduled_start: "2026-10-29T02:00:00Z",
      scheduled_end: "2026-10-29T04:00:00Z",
      description: "Upgrading to PostgreSQL 17",
    },
  ],
};

const ALL_OK = {
  app_name: "Healthy App",
  system_status: "all_operational" as const,
  components: [{ name: "API", status: "operational" as const, uptime_pct: 100 }],
  active_incidents: [],
  maintenance_windows: [],
};

describe("AppStatusPage", () => {
  it("renders system status banner", () => {
    const { container } = render(<AppStatusPage page={FULL_PAGE} />);
    expect(container.textContent).toContain("Minor System Issues");
  });

  it("renders all operational banner", () => {
    const { container } = render(<AppStatusPage page={ALL_OK} />);
    expect(container.textContent).toContain("All Systems Operational");
  });

  it("renders component names", () => {
    const { container } = render(<AppStatusPage page={FULL_PAGE} />);
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("Database");
  });

  it("renders component status labels", () => {
    const { container } = render(<AppStatusPage page={FULL_PAGE} />);
    expect(container.textContent).toContain("Operational");
    expect(container.textContent).toContain("Degraded");
    expect(container.textContent).toContain("Maintenance");
  });

  it("renders uptime percentages", () => {
    const { container } = render(<AppStatusPage page={FULL_PAGE} />);
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("98.5%");
  });

  it("renders active incidents", () => {
    const { container } = render(<AppStatusPage page={FULL_PAGE} />);
    expect(container.textContent).toContain("Active Incidents");
    expect(container.textContent).toContain("Webhook delays");
    expect(container.textContent).toContain("delivery delays");
  });

  it("hides incidents when empty", () => {
    const { container } = render(<AppStatusPage page={ALL_OK} />);
    expect(container.textContent).not.toContain("Active Incidents");
  });

  it("renders maintenance windows", () => {
    const { container } = render(<AppStatusPage page={FULL_PAGE} />);
    expect(container.textContent).toContain("Scheduled Maintenance");
    expect(container.textContent).toContain("DB Migration");
    expect(container.textContent).toContain("PostgreSQL 17");
  });

  it("hides maintenance when empty", () => {
    const { container } = render(<AppStatusPage page={ALL_OK} />);
    expect(container.textContent).not.toContain("Scheduled Maintenance");
  });

  it("renders component status dots", () => {
    const { container } = render(<AppStatusPage page={FULL_PAGE} />);
    expect(container.querySelector(".bg-green-500")).toBeTruthy();
    expect(container.querySelector(".bg-yellow-500")).toBeTruthy();
    expect(container.querySelector(".bg-blue-500")).toBeTruthy();
  });
});
