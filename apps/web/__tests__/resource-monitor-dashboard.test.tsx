import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResourceMonitorDashboard } from "@/components/resource-monitor-dashboard";

const mockCurrent = {
  timestamp: "2024-01-01T00:00:00Z", cpuPercent: 65.3,
  memoryMb: 180, diskMb: 300, networkBytes: 51200, activeConnections: 3,
};
const mockLimits = { cpuCores: 2, memoryMb: 256, diskMb: 512 };
const mockAlerts = [
  { id: "a1", resource: "cpu", level: "warning" as const, value: 75, message: "CPU at 75% (warning)", timestamp: "" },
];

describe("ResourceMonitorDashboard", () => {
  it("renders resource bars", () => {
    const { container } = render(
      <ResourceMonitorDashboard sandboxId="sb-1" current={mockCurrent}
        limits={mockLimits} alerts={[]} isThrottled={false} />
    );
    expect(container.textContent).toContain("65.3%");
    expect(container.textContent).toContain("180/256 MB");
    expect(container.textContent).toContain("50 KB");
  });

  it("shows throttled badge", () => {
    const { container } = render(
      <ResourceMonitorDashboard sandboxId="sb-1" current={mockCurrent}
        limits={mockLimits} alerts={[]} isThrottled={true} />
    );
    expect(container.textContent).toContain("THROTTLED");
  });

  it("shows alerts", () => {
    const { container } = render(
      <ResourceMonitorDashboard sandboxId="sb-1" current={mockCurrent}
        limits={mockLimits} alerts={mockAlerts} isThrottled={false} />
    );
    expect(container.textContent).toContain("CPU at 75%");
  });

  it("handles no data", () => {
    const { container } = render(
      <ResourceMonitorDashboard sandboxId="sb-1" current={null}
        limits={mockLimits} alerts={[]} isThrottled={false} />
    );
    expect(container.textContent).toContain("No data available");
  });
});
