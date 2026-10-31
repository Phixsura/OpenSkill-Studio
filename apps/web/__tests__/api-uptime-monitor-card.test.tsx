import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIUptimeMonitorCard from "../src/components/api-uptime-monitor-card";

const monitors = [
  { monitor_id: "m1", service_name: "API", uptime_pct: 99.95, consecutive_down: 0, total_checks: 1000 },
  { monitor_id: "m2", service_name: "Database", uptime_pct: 98.5, consecutive_down: 3, total_checks: 500 },
];

describe("APIUptimeMonitorCard", () => {
  it("renders header and down count", () => {
    const { container } = render(<APIUptimeMonitorCard monitors={monitors} appName="App" />);
    expect(container.textContent).toContain("Uptime Monitor");
    expect(container.textContent).toContain("1 down");
  });

  it("shows services and uptime", () => {
    const { container } = render(<APIUptimeMonitorCard monitors={monitors} appName="App" />);
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("98.5%");
  });

  it("shows empty state", () => {
    const { container } = render(<APIUptimeMonitorCard monitors={[]} appName="App" />);
    expect(container.textContent).toContain("No uptime monitors");
  });
});
