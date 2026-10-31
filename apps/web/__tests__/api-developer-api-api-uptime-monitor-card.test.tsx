import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiUptimeMonitorCard from "../src/components/api-developer-api-api-uptime-monitor-card";

const records = [
  { endpoint: "/api/users", uptime_pct: 99.95, total_downtime_minutes: 2.5 },
  { endpoint: "/api/payments", uptime_pct: 98.5, total_downtime_minutes: 45 },
];

describe("APIDeveloperAPIApiUptimeMonitorCard", () => {
  it("shows uptime data", () => {
    const { container } = render(<APIDeveloperAPIApiUptimeMonitorCard records={records} belowThresholdCount={1} appName="App" />);
    expect(container.textContent).toContain("Uptime Monitor");
    expect(container.textContent).toContain("1 below SLA");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("45m down");
  });
  it("shows all healthy", () => {
    const { container } = render(<APIDeveloperAPIApiUptimeMonitorCard records={[]} belowThresholdCount={0} appName="App" />);
    expect(container.textContent).toContain("all healthy");
  });
});
