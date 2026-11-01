import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import UptimeMonitorCard from "../src/components/uptime-monitor-card";

const services = [
  {
    service_id: "api",
    is_up: true,
    uptime_pct: 99.95,
    downtime_count: 2,
    last_downtime_reason: "",
  },
  {
    service_id: "db",
    is_up: false,
    uptime_pct: 98.5,
    downtime_count: 5,
    last_downtime_reason: "connection pool exhausted",
  },
  {
    service_id: "cache",
    is_up: true,
    uptime_pct: 100,
    downtime_count: 0,
    last_downtime_reason: "",
  },
];

describe("UptimeMonitorCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<UptimeMonitorCard services={services} appName="My App" />);
    expect(container.textContent).toContain("Uptime Monitor");
    expect(container.textContent).toContain("My App");
  });

  it("shows down count", () => {
    const { container } = render(<UptimeMonitorCard services={services} appName="App" />);
    expect(container.textContent).toContain("1 down");
  });

  it("shows all-up when healthy", () => {
    const up = services.filter((s) => s.is_up);
    const { container } = render(<UptimeMonitorCard services={up} appName="App" />);
    expect(container.textContent).toContain("All up");
  });

  it("renders service names and uptime", () => {
    const { container } = render(<UptimeMonitorCard services={services} appName="App" />);
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("db");
  });

  it("shows downtime reason", () => {
    const { container } = render(<UptimeMonitorCard services={services} appName="App" />);
    expect(container.textContent).toContain("connection pool exhausted");
  });

  it("shows outage count", () => {
    const { container } = render(<UptimeMonitorCard services={services} appName="App" />);
    expect(container.textContent).toContain("5 outages");
  });

  it("shows empty state", () => {
    const { container } = render(<UptimeMonitorCard services={[]} appName="App" />);
    expect(container.textContent).toContain("No services monitored");
  });
});
